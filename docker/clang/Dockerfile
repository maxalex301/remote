FROM ubuntu:16.04
LABEL maintainer="maxalex"

ARG clang_version="7.0.0"
ENV DEBIAN_FRONTEND=noninteractive
ENV apt_flags="-y --no-install-recommends --no-install-suggests"

RUN apt update -qq \
  && apt upgrade -y \
  && apt install ${apt_flags} xz-utils build-essential curl \
  && apt clean \
  && rm -rf /var/lib/apt/lists

RUN curl -SL http://releases.llvm.org/${clang_version}/clang+llvm-${clang_version}-x86_64-linux-gnu-ubuntu-16.04.tar.xz | tar -xJC /usr --strip-components=1

ENV \
    CC="/usr/bin/clang" \
    CXX="/usr/bin/clang++"
