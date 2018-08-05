import sys
import os
from server import Server, escape

class BuildEnv:
    def __init__(self, source_dir, build_dir, conan_dir):
        self.source_dir = source_dir
        self.build_dir = build_dir
        self.conan_dir = conan_dir
        self.project = os.path.basename(self.source_dir)
        self.cmake_lists = os.path.join(self.source_dir, 'CMakeLists.txt')
        self.cmake_cache = os.path.join(self.build_dir, 'CMakeCache.txt')
        self.conanfile_py = os.path.join(self.source_dir, 'conanfile.py')
        self.conanfile_txt = os.path.join(self.source_dir, 'conanfile.txt')
        self.project_cbp = os.path.join(self.build_dir, self.project+'.cbp')

class CMakeCommandBuilder:
    ninja_build_dir=None

    def __init__(self, source_dir, build_dir, config):
        self.source_dir = source_dir
        self.build_dir = build_dir
        self.config = config

    def __is_ninja_build(self):
        return self.config.NINJA is not None and self.config.NINJA

    def generate(self):
        command = ['cmake', '-G']
        command.append('Ninja' if self.__is_ninja_build() else 'Unix Makefiles')
        command.append(self.source_dir)
        command.append('-DCMAKE_C_COMPILER_LAUNCHER=' + self.config.COMPILER_LAUNCHER)
        command.append('-DCMAKE_CXX_COMPILER_LAUNCHER=' + self.config.COMPILER_LAUNCHER)
        command.append('-DCMAKE_C_COMPILER=' + self.config.CC)
        command.append('-DCMAKE_CXX_COMPILER=' + self.config.CXX)
        command.append('-DCMAKE_MAKE_PROGRAM=' + self.config.NINJA if self.__is_ninja_build() else '/usr/bin/make')
        print('Generate command: ' + command)
        return command

    def build(self):
        command = ['cmake', '--build', self.build_dir]
        print('Build command: ' + command)
        return command

    def install(self):
        command = self.build()
        command.append('--target')
        command.append('install')
        print('Install command: ' + command)
        return command

class RemoteBuilder:
    def __init__(self, config):
        self.__need_upload = True
        self.__need_download = True
        self.config = config
        self.server = Server(self.config.BUILD_HOST,
                             self.config.BUILD_PORT,
                             self.config.BUILD_USER)
        self.argv = sys.argv
        self.command = os.path.basename(self.argv[0])
        self.argv[0] = self.__command_replacer()

    def __command_replacer(self):
        if self.__is_conan():
            return self.config.CONAN
        elif self.__is_cmake():
            return self.config.CMAKE
        elif self.__is_make():
            return self.config.MAKE
        else:
            raise RuntimeError('Wrong command!!! Must be "conan", "cmake" or "make"')

    def __is_conan(self):
        return self.command == 'conan'

    def __is_cmake(self):
        return self.command == 'cmake'

    def __is_cmake_build(self):
        return self.__is_cmake() and '--build' in self.argv

    def __is_make(self):
        return self.command == 'make'

    def __is_toolset_check(self):
        return self.argv[-1].startswith('/private/') or self.argv[-1].startswith('/tmp/')

    def __is_version_check(self):
        return '-version' in self.argv or '--version' in self.argv or '-v' in self.argv


    def set_compiler_args(self):
        self.argv.insert(0, 'CC=' + self.config.CC)
        self.argv.insert(0, 'CXX=' + self.config.CXX)
        try:
            self.argv.insert(0, 'FC=' + self.config.FC)
        except:
            pass

    def create_remote_directories(self):
        self.server.mkdir(self.remote.source_dir)
        if os.path.exists(self.local.build_dir):
            self.server.mkdir(self.remote.build_dir)

    def upload_project(self):
        # if not self.__need_upload:
        #     return

        self.create_remote_directories()

        excludes = self.config.EXCLUDES
        if os.path.exists(self.local.build_dir):
            excludes.append(os.path.basename(self.local.build_dir))
        self.server.upload(self.local.source_dir, self.remote.source_dir, excludes)

    def download_artifacts(self):
        if os.path.exists(self.local.build_dir):
            self.server.download(self.remote.build_dir, self.local.build_dir, ['.ssh'])

    def before_run(self):
        if self.__is_cmake():
            self.argv[-1] = self.remote.source_dir
        if self.__is_cmake_build():
            self.argv[-1] = self.remote.build_dir

    def run(self):
        print(str(self.argv))
        return self.server.cmd_in_wd(self.remote.build_dir, ' '.join(escape(self.argv)))

    def replace_cache_variable_to(self, var, dst):
        self.server.replace_file_content(self.remote.cmake_cache, var + '=.*', var + '=' + dst)

    def modify_cmake_cache(self):
        self.replace_cache_variable_to('CMAKE_MAKE_PROGRAM:FILEPATH', self.config.MAKE)
        self.replace_cache_variable_to('CMAKE_C_COMPILER:FILEPATH', self.config.CC)
        self.replace_cache_variable_to('CMAKE_CXX_COMPILER:FILEPATH', self.config.CXX)

    def replace_file_variables(self, file):
        self.server.replace_file_content(file,
                                         '=' + self.remote.source_dir,
                                         '=' + self.local.source_dir)

    def after_run(self):
        if not self.__need_download:
            return

        if self.__is_cmake():
            self.replace_file_variables(self.remote.cmake_cache)
            if self.__is_toolset_check():
                self.modify_cmake_cache()

    def get_conan_home(self):
        try:
            return os.environ['CONAN_USER_HOME']
        except:
            return os.environ['HOME']
        # return conan_home

    def get_remote_conan_home(self):
        conan_home = self.server.getenv('CONAN_USER_HOME').decode("utf-8")
        if not conan_home or conan_home is None:
            return self.server.getenv('HOME').decode("utf-8")
        return conan_home

    def get_conan_source_dir(self):
        skip_next=False
        for arg in self.argv[2:]:
            if skip_next:
                skip_next=False
                continue

            if arg.startswith('-'):
                if '=' not in arg:
                    skip_next=True
                continue

            src_dir = os.path.abspath(arg)

            if os.path.exists(src_dir):
                return src_dir
        return None

    def make_configurations(self):
        src_dir = self.argv[-1]
        if self.__is_cmake_build():
            src_dir = os.path.dirname(os.path.abspath(self.argv[2]))
            self.__need_upload = False
        elif self.__is_conan():
            src_dir = self.get_conan_source_dir()
        elif self.__is_make():
            src_dir = os.getcwd()

        self.local = BuildEnv(os.path.abspath(src_dir),
                              os.getcwd(),
                              os.path.join(self.get_conan_home(), '.conan'))

        self.remote = BuildEnv(self.config.REMOTE_DIR + self.local.source_dir,
                               self.config.REMOTE_DIR + self.local.build_dir,
                               os.path.join(self.get_remote_conan_home(), '.conan'))
        print("remote: " + self.remote.source_dir + "   " + self.remote.build_dir)

    def execute(self):
        try:
            os.getcwd()
        except:
            raise RuntimeError('Wrong current directory!!!')

        if self.__is_version_check():
            self.server.cmd(' '.join(escape(self.argv)))
            return
        elif self.__is_conan() \
                and not 'install' in self.argv \
                and not 'build' in self.argv:
            self.server.cmd(' '.join(escape(self.argv)))
            return

        self.make_configurations()

        if self.__is_conan() \
                and not (os.path.exists(self.local.conanfile_py) \
                or os.path.exists(self.local.conanfile_txt)):
            raise RuntimeError("conanfile.py or conanfile.txt does not exists in source directory")
        elif self.__is_cmake() and not os.path.exists(self.local.cmake_lists):
            raise RuntimeError("CMakeLists.txt does not exists in source directory " + self.local.cmake_lists)

        print("Uploading project...")
        self.upload_project()

        self.set_compiler_args()

        self.before_run()
        if self.run() != 0:
            return
        self.after_run()

        print("Downloading artifacts...")
        self.download_artifacts()

        if self.__is_cmake() and self.__is_toolset_check():
            self.server.rm(self.remote.build_dir)
            self.server.rm(self.remote.source_dir)
