# We use Ubuntu 16.04 because there are already build binaries for this version of Ubuntu
# Check http://releases.llvm.org/7.0.0/ or http://releases.llvm.org/download.html#7.0.0 for the latest available binaries
FROM ubuntu:16.04

LABEL maintainer="maxalex"

# Make sure the image is updated, install some prerequisites,
# Download the latest version of Clang (official binary) for Ubuntu
# Extract the archive and add Clang to the PATH
RUN apt update -qq \
  && DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends xz-utils build-essential ca-certificates curl \
  && rm -rf /var/lib/apt/lists/* \
  && curl -C - -o /root/cmake.sh https://github.com/Kitware/CMake/releases/download/v3.13.1/cmake-3.13.1-Linux-x86_64.sh \
  && curl -C - -o /root/ninja.zip https://github.com/ninja-build/ninja/releases/download/v1.8.2/ninja-linux.zip \
  && curl -C - -SL http://releases.llvm.org/7.0.0/clang+llvm-7.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz \
  | tar -xJC . \
  && mv clang+llvm-7.0.0-x86_64-linux-gnu-ubuntu-16.04 clang_7.0.0 \
  && echo 'export PATH=/clang_7.0.0/bin:$PATH' >> ~/.bashrc \
  && echo 'export LD_LIBRARY_PATH=/clang_7.0.0/lib:LD_LIBRARY_PATH' >> ~/.bashrc

RUN \
  chmod +x /root/cmake.sh

ENV \
    CC="/usr/bin/clang" \
    CXX="/usr/bin/clang++"

# Start from a Bash prompt
CMD [ "/bin/bash" ]