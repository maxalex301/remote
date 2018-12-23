import sys, os
from server import Server, escape
from pathlib import Path

CLION_CMAKE_GENERATOR = 'CodeBlocks - Unix Makefiles'
CMAKE_CACHE_TXT = 'CMakeCache.txt'
CMAKE_COMMAND = 'cmake'
CMAKE_LISTS_TXT = 'CMakeLists.txt'
CONAN_COMMAND = 'conan'
CONAN_HOME = '.conan'
CONAN_PY = 'conanfile.py'
CONAN_TXT = 'conanfile.txt'
CONAN_BUILD_INFO = 'conanbuildinfo.cmake'
CONAN_INFO_TXT = 'conaninfo.txt'
NINJA_BUILD_DIR = 'cmake-build-ninja'
EXIT_SUCCESS = 0

class BuildEnv:
    def __init__(self, source_dir, build_dir):
        self.source_dir = source_dir
        self.build_dir = build_dir
        self.project = self.source_dir.name
        self.project_cbp = self.build_dir / (self.project + '.cbp')


class Command:
    def __init__(self, config):
        self.config = config
        self.argv = sys.argv
        self.env = dict()
        self.server = Server(self.config.BUILD_HOST,
                             self.config.BUILD_PORT,
                             self.config.BUILD_USER)
        self.need_clear_remote = False

    def is_version_check(self):
        return False

    def remote_command(self):
        return ''

    def check(self):
        return False

    def execute(self):
        if self.is_version_check():
            self.argv[0] = self.remote_command()
            self.server.cmd(' '.join(escape(self.argv)))
            return

        self.make_configurations()

        print("Uploading project...")
        self.upload_project()

        if self.run() != EXIT_SUCCESS:
            return

        print("Downloading artifacts...")
        self.download_artifacts()

        if self.need_clear_remote:
            print("Clear remote directories")
            self.server.rm(str(s/usr/local/bin/elf.remote.build_dir))
            self.server.rm(str(self.remote.source_dir))

    def run(self, command = ''):
        return self.server.cmd_in_wd(self.env, str(self.remote.build_dir), command if command else ' '.join(escape(self.argv)))

    def create_remote_directories(self):
        self.server.mkdir(str(self.remote.source_dir))
        if self.local.build_dir.exists():
            self.server.mkdir(str(self.remote.build_dir))

    def upload_project(self):
        self.create_remote_directories()

        excludes = self.config.EXCLUDES
        if self.local.build_dir.exists():
            excludes.append(self.local.build_dir.name)
        self.server.upload(str(self.local.source_dir), str(self.remote.source_dir), excludes)

    def download_artifacts(self):
        if self.local.build_dir.exists():
            self.server.download(str(self.remote.build_dir), str(self.local.build_dir), ['.ssh', '__pycache__'])


class CMakeCommand(Command):
    def __init__(self, config):
        super(CMakeCommand, self).__init__(config)

    @staticmethod
    def is_your():
        return Path(sys.argv[0]).name == CMAKE_COMMAND

    def remote_command(self):
        return self.config.CMAKE

    def __build_configuration(self):
        pass

    def __is_build(self):
        return '--build' in self.argv

    def __is_generate(self):
        return '-G' in self.argv

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
        # self.replace_cache_variable_to('CMAKE_GENERATOR:INTERNAL', CLION_CMAKE_GENERATOR)


    def replace_file_variables(self, file):
        self.server.replace_file_content(file,
                                         '=' + str(self.remote.source_dir),
                                         '=' + str(self.local.source_dir))


    def make_configurations(self):
        src_dir = Path(self.argv[-1]).resolve()
        if self.__is_build():
            src_dir = Path(self.argv[2]).resolve().parent
            self.__need_upload = False

        self.local = BuildEnv(src_dir, Path.cwd())

        remote = Path(self.config.REMOTE_DIR)
        print("Remote: " + str(remote))
        self.remote = BuildEnv(remote / str(self.local.source_dir)[1:], remote / str(self.local.build_dir)[1:])

        self.local.cmake_lists = Path(self.local.source_dir) / CMAKE_LISTS_TXT
        self.local.cmake_cache = Path(self.local.build_dir) / CMAKE_CACHE_TXT
        self.remote.cmake_cache = Path(self.remote.build_dir) / CMAKE_CACHE_TXT

        self.local.ninja_dir = self.local.build_dir.parent / NINJA_BUILD_DIR
        self.remote.ninja_dir = self.remote.build_dir.parent / NINJA_BUILD_DIR

        print("remote: " + str(self.remote.source_dir) + "   " + str(self.remote.build_dir))

    def run(self):
        assert self.local.cmake_lists.exists(), "CMakeLists.txt does not exists in source directory " + str(self.local.cmake_lists)

        self.argv[0] = self.config.CMAKE
        self.argv[-1] = str(self.remote.source_dir)

        if self.__is_build():
            if self.__is_ninja_build():
                self.local.build_dir = self.local.ninja_dir
                self.remote.build_dir = self.remote.ninja_dir
            self.argv = self.__build()
            self.argv.append('&&')
            self.argv += self.__install()
        elif self.__is_generate() and not self.__is_toolset_check():
            self.argv = self.__generate()

        res = super(CMakeCommand, self).run()
        if (res != EXIT_SUCCESS):
            return res

        self.modify_cmake_cache()

        if self.__is_toolset_check():
            self.replace_file_variables(self.remote.cmake_cache)
            self.need_clear_remote = True

        return res

    def __is_ninja_build(self):
        return self.config.NINJA is not None and self.config.NINJA

    def __generate(self):
        command = [self.config.CMAKE, '-DCMAKE_CXX_COMPILER=' + self.config.CXX]
        command += self.argv[1:]

        if (self.__is_ninja_build()):
            command += ['&&', 'mkdir', '-p', str(self.remote.ninja_dir), \
                        '&&', 'cd', str(self.remote.ninja_dir), \
                        '&&', 'cp', str(self.remote.build_dir / CONAN_BUILD_INFO), str(self.remote.ninja_dir), \
                        '&&', 'cp', str(self.remote.build_dir / CONAN_INFO_TXT), str(self.remote.ninja_dir), \
                        '&&', self.config.CMAKE, '-G', 'Ninja', \
                       '-DCMAKE_CXX_COMPILER=' + self.config.CXX, \
                       '-DCMAKE_MAKE_PROGRAM=' + self.config.NINJA
                       ]
            # Defines
            command += [arg for arg in self.argv if arg.startswith('-D')]

            if self.config.COMPILER_LAUNCHER:
                command.append('-DCMAKE_CXX_COMPILER_LAUNCHER=' + self.config.COMPILER_LAUNCHER)
            command.append(str(self.remote.source_dir))

        return command

    def __build(self, target=''):
        build_cmd = [self.config.CMAKE, '--build', str(self.remote.build_dir)]
        if target:
            build_cmd.append('--target')
            build_cmd.append(target)

        if self.config.NINJA_FLAGS is not None:
            build_cmd.append('--')
            build_cmd.append(self.config.NINJA_FLAGS)
        print("Build command: {}".format(build_cmd))
        return build_cmd

    def __install(self):
        return self.__build(target='install')


class ConanCommand(Command):
    @staticmethod
    def is_your():
        return Path(sys.argv[0]).name == CONAN_COMMAND

    def remote_command(self):
        return self.config.CONAN

    def is_version_check(self):
        return '-v' in self.argv or '--version' in self.argv

    def run(self):
        self.argv[0] = self.config.CONAN
        super(ConanCommand, self).run()

    def check(self):
        self.conanfile_py = Path(self.local.source_dir) / CONAN_PY
        self.conanfile_txt = Path(self.local.source_dir) / CONAN_TXT
        assert self.conanfile_py.exists() or self.conanfile_txt.exists(), "conanfile.py or conanfile.txt does not exists in source directory"

    def get_home(self):
        try:
            return Path(os.environ['CONAN_USER_HOME']).resolve()
        except:
            return Path.home()

    def make_configurations(self):
        self.local = BuildEnv(self.get_source_dir(), Path(os.getcwd()))
        self.local.conan_dir = self.get_home() / CONAN_HOME

        remote = Path(self.config.REMOTE_DIR)
        self.remote = BuildEnv(remote / self.local.source_dir, remote / self.local.build_dir)
        self.remote.conan_dir = self.get_remote_home() / CONAN_HOME
        print("remote: " + str(self.remote.source_dir) + "   " + str(self.remote.build_dir))

    def get_remote_home(self):
        # conan_home = self.server.getenv('CONAN_USER_HOME').decode("utf-8")
        # if not conan_home or conan_home is None:
            return Path().home()
        # return Path(conan_home).resolve()

    def __arg_generator(self):
        i=2
        while i < len(self.argv):
            if self.argv[i].startswith('-'):
                i += ('=' not in arg) + 1
                continue
            yield self.argv[i]
            i += 1

    def get_source_dir(self):
        for arg in self.__arg_generator():
            src_dir = Path(arg).resolve()
            if src_dir.exists():
                return src_dir
        return None
