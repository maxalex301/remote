import sys
import os
from server import Server, escape

class BuildEnv:
    def __init__(self, base_path, project_name, build_dir):
        self.project_dir = os.path.join(base_path, project_name)
        self.build_dir = os.path.join(self.project_dir, build_dir)
        self.conan_dir = ''

class RemoteBuilder:
    def __init__(self, config):
        self.config = config
        self.server = Server(self.config.BUILD_HOST,
                             self.config.BUILD_PORT,
                             self.config.BUILD_USER)
        self.argv = sys.argv
        self.command = os.path.basename(self.argv[0])
        self.argv[0] = self.command_replacer()

    def command_replacer(self):
        if self.command == 'conan':
            return self.config.CONAN
        elif self.command == 'cmake':
            return self.config.CMAKE
        elif self.command == 'make':
            return self.config.MAKE
        else:
            raise RuntimeError('Wrong command!!! Must be "conan", "cmake" or "make"')

    def check_current_directory(self):
        return os.getcwd().startswith(os.getenv("HOME"))

    def set_compiler_args(self):
        self.argv.insert(0, 'CC=' + self.config.CC)
        self.argv.insert(0, 'CXX=' + self.config.CXX)
        try:
            if self.config.FC:
                self.argv.insert(0, 'FC=' + self.config.FC)
        except:
            pass

    def extract_dir_and_project(self):
        dir = os.path.normpath(os.getcwd())
        if os.path.basename(dir) == self.config.BUILD_DIR:
            dir = os.path.dirname(dir)
        return os.path.split(dir)

    def create_remote_directories(self):
        self.server.mkdir(self.remote.project_dir)
        if os.path.exists(self.local.build_dir):
            self.server.mkdir(self.remote.build_dir)

    def upload_project(self):
        excludes = self.config.EXCLUDES
        if os.path.exists(self.local.build_dir):
            excludes.append(self.config.BUILD_DIR)
        self.server.upload(self.local.project_dir, self.remote.project_dir, excludes)

    def download_artifacts(self):
        if os.path.exists(self.local.build_dir):
            self.server.download(self.remote.build_dir, self.local.build_dir, ['.ssh'])

    def before_run(self):
        if self.command == 'conan':
            self.local.conan_dir = self.config.CONANHOME
            self.remote.conan_dir = self.config.REMOTE_DIR
            self.argv.insert(0, 'HOME=' + self.remote.conan_dir)
        elif self.command == 'cmake':
            if (self.argv[-1] == self.local.project_dir):
                self.argv[-1] = self.remote.project_dir

    def run(self):
        dir = self.remote.build_dir if os.path.exists(self.local.build_dir) else self.remote.project_dir
        return self.server.cmd_in_wd(dir, ' '.join(escape(self.argv)))

    def after_run(self):
        if self.command == 'conan' and 'info' not in self.argv:
            self.server.download(self.remote.conan_dir, self.local.conan_dir, [])

    def tools_version_check(self):
        self.server.cmd(' '.join(escape(self.argv)))
        raise RuntimeError('argv: '+str(self.argv))

    def clion_toolset_check(self, path):
        dest_dir = os.path.join(self.config.REMOTE_DIR, 'clion-toolset-check')
        dest_cwd = os.path.join(dest_dir, '_build')
        self.argv[-1] = dest_dir
        self.server.upload(path, dest_dir, [])
        self.server.cmd_in_wd(dest_cwd, ' '.join(escape(self.argv)))
        cmake_cache_file = os.path.join(dest_cwd, "CMakeCache.txt");
        self.server.replace_file_content(cmake_cache_file, '='+path, '='+dest_dir)
        self.server.replace_file_content(cmake_cache_file,
                                         'CMAKE_MAKE_PROGRAM:FILEPATH=.*',
                                         'CMAKE_MAKE_PROGRAM:FILEPATH='+self.config.MAKE)
        self.server.replace_file_content(cmake_cache_file,
                                         'CMAKE_C_COMPILER:FILEPATH=s.*',
                                         'CMAKE_C_COMPILER:FILEPATH='+self.config.CC)
        self.server.replace_file_content(cmake_cache_file,
                                         'CMAKE_CXX_COMPILER:FILEPATH=.*',
                                         'CMAKE_CXX_COMPILER:FILEPATH='+self.config.CXX)
        self.server.download(dest_dir, path, [])
        self.server.rm(dest_dir)

    def no_build_execute(self):
        if self.argv[1] == '-version':
            self.tools_version_check()
        elif self.argv[-1].startswith('/private/'):
            self.clion_toolset_check(self.argv[-1])

    def execute(self):
        if not self.check_current_directory():
            self.no_build_execute()
            return

        [base, self.project] = self.extract_dir_and_project()
        self.local = BuildEnv(base,
                              self.project,
                              self.config.BUILD_DIR)
        self.remote = BuildEnv(self.config.REMOTE_DIR,
                               self.project,
                               self.config.BUILD_DIR)

        self.create_remote_directories()
        self.upload_project()
        self.set_compiler_args()

        self.before_run()
        if self.run() != 0:
            return
        self.after_run()

        self.download_artifacts()
