# We use Ubuntu 16.04 because there are already build binaries for this version of Ubuntu
# Check http://releases.llvm.org/7.0.0/ or http://releases.llvm.org/download.html#7.0.0 for the latest available binaries
FROM ubuntu:16.04
LABEL maintainer="maxalex"

ARG clang_version="7.0.0"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update -qq \
  && apt upgrade -y \
  && apt install -y  --no-install-recommends --no-install-suggests \
    xz-utils build-essential curl
#  && rm -rf /var/lib/apt/lists

#COPY clang+llvm-${clang_version}-x86_64-linux-gnu-ubuntu-16.04.tar.xz /tmp/clang+llvm-${clang_version}-x86_64-linux-gnu-ubuntu-16.04.tar.xz
#RUN tar -xJf /tmp/clang+llvm-${clang_version}-x86_64-linux-gnu-ubuntu-16.04.tar.xz -C /usr --strip-components=1 \
#    && rm -f /tmp/clang+llvm-${clang_version}-x86_64-linux-gnu-ubuntu-16.04.tar.xz

RUN curl -SL http://releases.llvm.org/${clang_version}/clang+llvm-${clang_version}-x86_64-linux-gnu-ubuntu-16.04.tar.xz | tar -xJC /usr --strip-components=1

ENV \
    CC="/usr/bin/clang" \
    CXX="/usr/bin/clang++"
