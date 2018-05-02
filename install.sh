#!/bin/sh
mkdir -p bin
cd bin
ln -sf ../src/cmd.py conan
ln -sf ../src/cmd.py cmake
ln -sf ../src/cmd.py make
chmod 555 conan
chmod 555 cmake
chmod 555 make
export PATH=$(pwd):$PATH
cd ../
