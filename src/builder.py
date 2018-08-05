import sys
import os
from command import CMakeCommand, ConanCommand

class BuildEnv:
    def __init__(self, source_dir, build_dir, conan_dir):
        self.source_dir = source_dir
        self.build_dir = build_dir
        self.conan_dir = conan_dir
        self.project = os.path.basename(self.source_dir)
        self.project_cbp = os.path.join(self.build_dir, self.project+'.cbp')


class RemoteBuilder:
    def __init__(self, config):
        self.__need_upload = True
        self.__need_download = True
        self.config = config

        self.argv = sys.argv
        self.command = self.__command_searcher()


    def __command_searcher(self):
        if CMakeCommand.is_your(sys.argv):
            return CMakeCommand(sys.argv)
        elif ConanCommand.is_your(sys.argv):
            return ConanCommand(sys.argv)
        else:
            raise RuntimeError('Wrong command!!! Must be "conan" or "cmake"')


    def create_remote_directories(self):
        self.server.mkdir(self.remote.source_dir)
        if os.path.exists(self.local.build_dir):
            self.server.mkdir(self.remote.build_dir)




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

        if self.command.is_version_check():
            self.server.cmd(' '.join(escape(self.argv)))
            return
        elif self.__is_conan() \
                and not 'install' in self.argv \
                and not 'build' in self.argv:
            self.server.cmd(' '.join(escape(self.argv)))
            return

        self.make_configurations()

        if self.__is_conan() \


        print("Uploading project...")
        self.upload_project()

        self.set_compiler_args()

        self.before_run()
        if self.run() != 0:
            return
        self.after_run()

        print("Downloading artifacts...")
        self.download_artifacts()
