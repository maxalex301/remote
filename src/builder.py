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
        self.conanfile = os.path.join(self.source_dir, 'conanfile.py')


class RemoteBuilder:
    def __init__(self, config):
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

    def __is_make(self):
        return self.command == 'make'

    def set_compiler_args(self):
        self.argv.insert(0, 'CC=' + self.config.CC)
        self.argv.insert(0, 'CXX=' + self.config.CXX)
        try:
            if self.config.FC:
                self.argv.insert(0, 'FC=' + self.config.FC)
        except:
            pass

    def create_remote_directories(self):
        self.server.mkdir(self.remote.source_dir)
        if os.path.exists(self.local.build_dir):
            self.server.mkdir(self.remote.build_dir)

    def upload_project(self):
        excludes = self.config.EXCLUDES
        if os.path.exists(self.local.build_dir):
            excludes.append(os.path.basename(self.local.build_dir))
        self.server.upload(self.local.source_dir, self.remote.source_dir, excludes)

    def download_artifacts(self):
        if os.path.exists(self.local.build_dir):
            self.server.download(self.remote.build_dir, self.local.build_dir, ['.ssh'])

    def before_run(self):
        if self.__is_conan():
            self.argv.insert(0, 'HOME=' + self.config.REMOTE_DIR)
        elif self.__is_cmake():
            self.argv[-1] = self.remote.source_dir

    def run(self):
        return self.server.cmd_in_wd(self.remote.build_dir, ' '.join(escape(self.argv)))

    def after_run(self):
        if self.__is_cmake():
            self.server.replace_file_content(self.remote.cmake_cache,
                                             '=' + self.remote.source_dir,
                                             '=' + self.local.source_dir)
            if self.__is_toolset_check():
                self.server.replace_file_content(self.remote.cmake_cache,
                                                 'CMAKE_MAKE_PROGRAM:FILEPATH=.*',
                                                 'CMAKE_MAKE_PROGRAM:FILEPATH=' + self.config.MAKE)
                self.server.replace_file_content(self.remote.cmake_cache,
                                                 'CMAKE_C_COMPILER:FILEPATH=.*',
                                                 'CMAKE_C_COMPILER:FILEPATH=' + self.config.CC)
                self.server.replace_file_content(self.remote.cmake_cache,
                                                 'CMAKE_CXX_COMPILER:FILEPATH=.*',
                                                 'CMAKE_CXX_COMPILER:FILEPATH=' + self.config.CXX)

        if self.__is_conan() and 'info' not in self.argv:
            self.server.download(self.remote.conan_dir, self.local.conan_dir, [])

    def __is_toolset_check(self):
        return self.argv[-1].startswith('/private/') or self.argv[-1].startswith('/tmp/')

    def make_configurations(self):
        src_dir = self.argv[-1]
        if self.__is_conan():
            src_dir = self.argv[2]

        self.local = BuildEnv(os.path.abspath(src_dir),
                              os.getcwd(),
                              os.path.join(self.config.CONANHOME, '.conan'))

        self.remote = BuildEnv(os.path.join(self.config.REMOTE_DIR, self.local.source_dir),
                               os.path.join(self.config.REMOTE_DIR, self.local.build_dir),
                               os.path.join(self.config.REMOTE_DIR, '.conan'))

    def execute(self):
        if self.__is_cmake() and '-version' in self.argv:
            self.server.cmd(' '.join(escape(self.argv)))
            return

        self.make_configurations()

        if self.__is_conan() and not os.path.exists(self.local.conanfile):
            raise RuntimeError("conanfile.py does not exists in source directory")
        elif self.__is_cmake() and not os.path.exists(self.local.cmake_lists):
            raise RuntimeError("CMakeLists.txt does not exists in source directory")

        self.create_remote_directories()
        self.upload_project()

        self.set_compiler_args()

        self.before_run()
        if self.run() != 0:
            return
        self.after_run()

        self.download_artifacts()

        if self.__is_cmake() and self.__is_toolset_check():
            self.server.rm(self.remote.build_dir)
            self.server.rm(self.remote.source_dir)
