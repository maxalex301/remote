# We use Ubuntu 16.04 because there are already build binaries for this version of Ubuntu
# Check http://releases.llvm.org/7.0.0/ or http://releases.llvm.org/download.html#7.0.0 for the latest available binaries
FROM clang-base:latest
LABEL maintainer="maxalex"

RUN DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends distcc
#  && rm -rf /var/lib/apt/lists/*
