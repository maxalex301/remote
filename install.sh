#!/bin/sh
mkdir -p bin
PYTHON3_PATH=$(which python3)
sed -e s#/usr/bin/python3#${PYTHON3_PATH}#g src/cmd.py.tmpl > src/cmd.py
ln -sf src/cmd.py bin/conan
ln -sf src/cmd.py bin/cmake
ln -sf src/cmd.py bin/make
chmod 555 bin/conan
chmod 555 bin/cmake
chmod 555 bin/make
export PATH=$(pwd)/bin:$PATH
