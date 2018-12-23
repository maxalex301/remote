FROM gcc:latest
LABEL maintainer="maxalex"

ARG clang_version="7.0.0"
ENV DEBIAN_FRONTEND=noninteractive \
    LLVM_VERSION=7.0 \
    apt_flags="-y --no-install-recommends --no-install-suggests"

RUN curl -SL http://releases.llvm.org/${clang_version}/clang+llvm-${clang_version}-x86_64-linux-gnu-ubuntu-16.04.tar.xz | tar -xJC /usr/local --strip-components=1
RUN ldconfig /usr/local/lib
