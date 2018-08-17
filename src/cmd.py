#!/usr/bin/python
from conf import config
import os
from command import CMakeCommand, ConanCommand

def command_searcher(self):
    if CMakeCommand.is_your():
        return CMakeCommand(config)
    elif ConanCommand.is_your():
        return ConanCommand(config)
    return None

if __name__ == '__main__':
    assert os.getcwd(), 'Wrong current directory!!!'
    self.command = self.__command_searcher()
    assert self.command is not None, 'Unknown command, use conan or cmake'
    self.command.execute()
