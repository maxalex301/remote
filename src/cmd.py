#!/usr/bin/python
from builder import RemoteBuilder
from conf import config
import sys
import os

if __name__ == '__main__':
    builder = RemoteBuilder(config)
    builder.execute()
