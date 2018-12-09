FROM gcc-clang:latest
LABEL maintainer="maxalex"

ARG cmake_version=3.13.1
ARG ninja_version=1.8.2

# Install packages
RUN apt-get update -qq \
    && apt-get upgrade -y \
    && apt-get install ${apt_flags} unzip ca-certificates distcc python3-dev python3-pip python3-setuptools \

# Install build tools: cmake, ninja, conan
RUN curl -SL https://github.com/Kitware/CMake/releases/download/v${cmake_version}/cmake-${cmake_version}-Linux-x86_64.tar.gz | tar -xzC /usr/local --strip-components=1 \
    && curl -L -o /tmp/ninja-linux.zip https://github.com/ninja-build/ninja/releases/download/v${ninja_version}/ninja-linux.zip \
    && unzip /tmp/ninja-linux.zip -d /usr/local/bin \
    && rm -f /tmp/ninja-linux.zip \
    && pip3 install --upgrade pip \
    && pip install conan

# Clean apt cache
RUN apt remove -y unzip xz-utils curl \
    && apt autoremove -y \
    && apt clean \
    && rm -rf /var/lib/apt/lists

# Configure Conan
RUN conan profile new --detect clang \
    && conan profile update env.CC=/usr/local/bin/clang clang \
    && conan profile update env.CXX=/usr/local/bin/clang++ clang \
    && conan profile update env.FC=/usr/local/bin/gfortran clang \
    && conan profile update settings.compiler=clang clang \
    && conan profile update settings.compiler.version=7 clang \
    && conan profile update settings.build_type=Release clang \
    && conan profile update settings.cppstd=17 clang
    && conan profile new --detect gcc \
    && conan profile update env.CC=/usr/local/bin/gcc gcc \
    && conan profile update env.CXX=/usr/local/bin/g++ gcc \
    && conan profile update env.FC=/usr/local/bin/gfortran gcc \
    && conan profile update settings.compiler=gcc clang \
    && conan profile update settings.compiler.version=8 clang \
    && conan profile update settings.build_type=Release gcc \
    && conan profile update settings.cppstd=17 gcc
    && ln -s /root/.conan/profiles/clang /root/.conan/profiles/default

# Environment variables
ENV CONAN_CMAKE_GENERATOR="Ninja" \
    CONAN_CPU_COUNT=2 \
    CONAN_MAKE_PROGRAM="/usr/bin/ninja"