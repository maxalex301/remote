#!/usr/bin/python
from builder import RemoteBuilder
from conf import config
import sys
import os

if __name__ == '__main__':
    log = open('/tmp/cmd.log', 'a')
    log.write('argv: ' + str(sys.argv) + '\n')
    log.write('cwd: ' + os.getcwd() + '\n')
    log.close()
    builder = RemoteBuilder(config)
    builder.execute()
