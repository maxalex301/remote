# We use Ubuntu 16.04 because there are already build binaries for this version of Ubuntu
# Check http://releases.llvm.org/7.0.0/ or http://releases.llvm.org/download.html#7.0.0 for the latest available binaries
FROM ubuntu:16.04
LABEL maintainer="maxalex"

COPY clang+llvm-7.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz /tmp/clang+llvm-7.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz

RUN apt update -qq \
  && apt upgrade -y \
  && DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
    xz-utils build-essential curl
#  && rm -rf /var/lib/apt/lists/*

RUN tar -xJf /tmp/clang+llvm-7.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz -C /usr
#  && curl -SL http://releases.llvm.org/7.0.0/clang+llvm-7.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz | tar -xJC /usr --strip-components=1

ENV \
    CC="/usr/bin/clang" \
    CXX="/usr/bin/clang++"
