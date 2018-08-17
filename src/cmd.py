#!/usr/bin/python
from builder import RemoteBuilder
from conf import config

if __name__ == '__main__':
    RemoteBuilder(config).execute()
