import sys
from server import Server, escape

class Command:
    def __init__(self, config):
        self.config = config
        self.argv = sys.argv
        self.server = Server(self.config.BUILD_HOST,
                             self.config.BUILD_PORT,
                             self.config.BUILD_USER)

    def is_version_check(self):
        return False

    def remote_command(self):
        return ''

    def check(self):
        return False

    def run(self):
        return self.server.cmd_in_wd(self.remote.build_dir, ' '.join(escape(self.argv)))

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



class CMakeCommandParser(Command):
    def __init__(self):
        self.cmake_lists = os.path.join(self.source_dir, 'CMakeLists.txt')
        self.cmake_cache = os.path.join(self.build_dir, 'CMakeCache.txt')

    @staticmethod
    def is_your():
        return sys.argv[0] == 'cmake'


    def __is_build(self):
        return '--build' in self.argv


    def is_version_check(self):
        return '-version' in self.argv or '--version' in self.argv


    def __is_toolset_check(self):
        return self.argv[-1].startswith('/private/') or self.argv[-1].startswith('/tmp/')


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

    def check(self):
        if not os.path.exists(self.local.cmake_lists):
            raise RuntimeError("CMakeLists.txt does not exists in source directory " + self.local.cmake_lists)


    def run(self):
        self.argv[-1] = self.remote.source_dir
        if self.__is_cmake_build():
            self.argv[-1] = self.remote.build_dir

        self.argv[0] = self.config.CMAKE

        self.replace_file_variables(self.remote.cmake_cache)

        if self.__is_toolset_check():
            self.modify_cmake_cache()
            self.server.rm(self.remote.build_dir)
            self.server.rm(self.remote.source_dir)

    def __is_ninja_build(self):
        return self.config.NINJA is not None and self.config.NINJA

    def __command_str(self, command):
        return ' '.join(command)

    def __generate(self):
        command = [self.config.CMAKE, '-G', \
                   'Ninja' if self.__is_ninja_build() else 'Unix Makefiles', \
                   self.source_dir, \
                   '-DCMAKE_C_COMPILER_LAUNCHER=' + self.config.COMPILER_LAUNCHER, \
                   '-DCMAKE_CXX_COMPILER_LAUNCHER=' + self.config.COMPILER_LAUNCHER, \
                   '-DCMAKE_C_COMPILER=' + self.config.CC, \
                   '-DCMAKE_CXX_COMPILER=' + self.config.CXX, \
                   '-DCMAKE_MAKE_PROGRAM=' + self.config.NINJA if self.__is_ninja_build() else self.config.MAKE
                   ]
        return self.__command_str(command)

    def __build(self):
        command = [self.config.CMAKE, '--build', self.build_dir]
        return self.__command_str(command)

    def __install(self):
        command = self.__build()
        command.append('--target')
        command.append('install')
        return self.__command_str(command)

    def __build_command(self):
        return '{gen} && {build} && {install}'.format(gen=self.__generate(), build=self.__build(), install=self.__generate())


class ConanCommand(Command):
    @staticmethod
    def is_your(argv):
        return argv[0] == 'conan'

    def is_version_check(self):
        return '-v' in self.argv or '--version' in self.argv

    def run(self):
        self.argv[0] = self.config.CONAN

    def check(self):
        self.conanfile_py = os.path.join(self.source_dir, 'conanfile.py')
        self.conanfile_txt = os.path.join(self.source_dir, 'conanfile.txt')
        if not (os.path.exists(self.local.conanfile_py) \
            or os.path.exists(self.local.conanfile_txt)):
            raise RuntimeError("conanfile.py or conanfile.txt does not exists in source directory")

    def get_conan_home(self):
        try:
            return os.environ['CONAN_USER_HOME']
        except:
            return os.environ['HOME']


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
