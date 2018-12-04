# We use Ubuntu 16.04 because there are already build binaries for this version of Ubuntu
# Check http://releases.llvm.org/7.0.0/ or http://releases.llvm.org/download.html#7.0.0 for the latest available binaries
FROM clang-base:latest
LABEL maintainer="maxalex"

RUN DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
    unzip ca-certificates curl distcc python3-pip python3-setuptools
#  && rm -rf /var/lib/apt/lists/*

RUN curl -SL https://github.com/Kitware/CMake/releases/download/v3.13.1/cmake-3.13.1-Linux-x86_64.tar.gz | tar -xzC /usr --strip-components=1 \
  && curl -L -o /tmp/ninja-linux.zip https://github.com/ninja-build/ninja/releases/download/v1.8.2/ninja-linux.zip \
  && unzip /tmp/ninja-linux.zip -d /usr/bin \
  && rm -f /tmp/ninja-linux.zip
  && pip3 install --upgrade pip \
  && pip install conan