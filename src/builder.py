import sys
import os
from command import CMakeCommand, ConanCommand



class RemoteBuilder:
    def __init__(self, config):
        self.__need_upload = True
        self.__need_download = True
        self.config = config
        self.argv = sys.argv

    def __command_searcher(self):
        if CMakeCommand.is_your(sys.argv):
            return CMakeCommand(sys.argv)
        elif ConanCommand.is_your(sys.argv):
            return ConanCommand(sys.argv)
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
        assert os.getcwd(), 'Wrong current directory!!!'
        self.command = self.__command_searcher()
        assert self.command is not None, 'Unknown command, use conan or cmake'


