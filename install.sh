#!/bin/sh
function add_binary {
    ln -sf ../src/cmd.py $1
    chmod 555 $1
}

PYTHON3_PATH=$(which python3)
sed -e s#/usr/bin/python3#${PYTHON3_PATH}#g src/cmd.py.tmpl > src/cmd.py

mkdir -p bin
cd bin
add_binary conan
add_binary cmake
cd -
export PATH=$(pwd)/bin:$PATH
