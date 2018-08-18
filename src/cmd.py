#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
import os, sys
from conf import config
from command import CMakeCommand, ConanCommand
from pathlib import Path

def command_searcher():
    # if CMakeCommand.is_your():
        return CMakeCommand(config)
    # elif ConanCommand.is_your():
    #     return ConanCommand(config)
    # return None

if __name__ == '__main__':
    assert os.getcwd(), 'Wrong current directory!!!'
    command = command_searcher()
    assert command is not None, 'Unknown command [' + Path(sys.argv[0]).name + '], use conan or cmake'
    command.execute()
