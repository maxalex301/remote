FROM maxalex/gcc-clang:latest
LABEL maintainer="maxalex"

ARG cmake_version=3.13.2
ARG python_version=3.7.1
ARG cmake_url=https://github.com/Kitware/CMake/releases/download/v${cmake_version}/cmake-${cmake_version}-Linux-x86_64.tar.gz
ARG ninja_url=https://github.com/Kitware/ninja/releases/download/v1.8.2.g81279.kitware.dyndep-1.jobserver-1/ninja-1.8.2.g81279.kitware.dyndep-1.jobserver-1_x86_64-linux-gnu.tar.gz
ARG python_url=https://www.python.org/ftp/python/${python_version}/Python-${python_version}.tar.xz
#ARG python_url=https://www.python.org/ftp/python/3.7.1/Python-3.7.1.tar.xz
# Install packages
RUN apt-get update -qq \
    && apt-get upgrade -y \
    && apt remove -y python2.7 python2.7-minimal python3 python3-minimal \
    && apt autoremove -y \
    && apt-get install ${apt_flags} ca-certificates distcc

# Install build tools: cmake, ninja, conan
RUN curl -SL ${cmake_url} | tar -xzC /usr/local --strip-components=1 \
    && curl -SL ${ninja_url} | tar -xzC /usr/local/bin --strip-components=1

# Install python
RUN mkdir -p /tmp/python \
    && curl -SL ${python_url} | tar -xJC /tmp/python --strip-components=1 \
    && cd /tmp/python \
    && ./configure --enable-optimizations \
    && make altinstall \
    && rm -rf /tmp/python \
    && update-alternatives --install /usr/bin/python python /usr/local/bin/python3.7 10 \
    && update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.7 10

# Clean apt cache
RUN apt remove -y xz-utils curl \
    && apt autoremove -y \
    && apt clean \
    && rm -rf /var/lib/apt/lists

## Configure Conan
RUN pip install conan \
    && conan profile new --detect temp \
    && conan profile update settings.build_type=Release temp \
    && conan profile update settings.cppstd=17 temp \
    && conan profile update env.FC=/usr/local/bin/gfortran temp \
    && cp /root/.conan/profiles/temp /root/.conan/profiles/clang \
    && cp /root/.conan/profiles/temp /root/.conan/profiles/gcc \
    && rm -f /root/.conan/profiles/temp \
    && conan profile update env.CC=/usr/local/bin/clang clang \
    && conan profile update env.CXX=/usr/local/bin/clang++ clang \
    && conan profile update settings.compiler=clang clang \
    && conan profile update settings.compiler.version=7.0 clang \
    && conan profile update settings.compiler.libcxx=libc++ clang \
    && conan profile update env.CC=/usr/local/bin/gcc gcc \
    && conan profile update env.CXX=/usr/local/bin/g++ gcc \
    && conan profile update settings.compiler=gcc gcc \
    && conan profile update settings.compiler.version=8.2 gcc \
    && conan profile update settings.compiler.libcxx=libstdc++ gcc \
    && ln -s /root/.conan/profiles/clang /root/.conan/profiles/default

## Environment variables
ENV CONAN_CMAKE_GENERATOR="Ninja" \
    CONAN_CPU_COUNT=2 \
    CONAN_MAKE_PROGRAM="/usr/local/bin/ninja"
