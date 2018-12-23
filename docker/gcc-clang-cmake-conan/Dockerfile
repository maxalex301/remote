FROM maxalex/gcc-clang:latest
LABEL maintainer="maxalex"

ARG cmake_version=3.13.2
ARG cmake_url=https://github.com/Kitware/CMake/releases/download/v${cmake_version}/cmake-${cmake_version}-Linux-x86_64.tar.gz
ARG ninja_url=https://github.com/Kitware/ninja/releases/download/v1.8.2.g81279.kitware.dyndep-1.jobserver-1/ninja-1.8.2.g81279.kitware.dyndep-1.jobserver-1_x86_64-linux-gnu.tar.gz
ARG python_version=3.7.1
ARG python_url=https://www.python.org/ftp/python/${python_version}/Python-${python_version}.tar.xz
ARG python_dir=/tmp/python
ARG distcc_version=3.3.2
ARG distcc_url=https://github.com/distcc/distcc/archive/v${distcc_version}.zip
ARG distcc_dir=/tmp/distcc
ARG ccache_version=3.5
ARG ccache_url=https://www.samba.org/ftp/ccache/ccache-${ccache_version}.tar.gz
ARG ccache_dir=/tmp/ccache
ARG install_prefix=/usr/local

# Install packages
RUN apt-get update -qq \
    && apt-get upgrade -y \
    && apt-get install ${apt_flags} bsdtar libiberty-dev

# Download tools: cmake, ninja, python, distcc, cache
RUN curl -kSL ${cmake_url} | bsdtar -xf- -C ${install_prefix} --strip-components=1 \
    && curl -kSL ${ninja_url} | bsdtar -xf- -C ${install_prefix}/bin --strip-components=1 \
    && mkdir -p ${python_dir} \
    && curl -kSL ${python_url} | bsdtar -xf- -C ${python_dir} --strip-components=1 \
    && mkdir -p ${distcc_dir} \
    && curl -kSL ${distcc_url} | bsdtar -xf- -C ${distcc_dir} --strip-components=1 \
    && mkdir -p ${ccache_dir} \
    && curl -kSL ${ccache_url} | bsdtar -xf- -C ${ccache_dir} --strip-components=1

# Clean apt cache
RUN apt remove -y xz-utils curl python2.7 python2.7-minimal python3 python3-minimal bsdtar \
    && apt autoremove -y \
    && apt clean \
    && rm -rf /var/lib/apt/lists

# Install python
RUN cd ${python_dir} \
    && ./configure --enable-optimizations --prefix=${install_prefix} \
    && make altinstall \
    && rm -rf ${python_dir} \
    && update-alternatives --install /usr/bin/python python /usr/local/bin/python3.7 10 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.7 10 \
    && update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.7 10 \
    && update-alternatives --install /usr/bin/pip3 pip3 /usr/local/bin/pip3.7 10

# Install ccache and distcc
RUN cd ${distcc_dir} \
    && chmod +x autogen.sh \
    && ./autogen.sh \
    && ./configure --prefix=${install_prefix} CFLAGS="-Wno-error" \
    && make install \
    && rm -rf ${distcc_dir} \
    && cd ${ccache_dir} \
    && ./configure --prefix=${install_prefix} \
    && make install \
    && rm -rf ${ccache_dir}


# Configure Conan
RUN pip install -q --no-cache-dir conan \
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

# Environment variables
ENV CONAN_CMAKE_GENERATOR="Ninja" \
    CONAN_CPU_COUNT=2 \
    CONAN_MAKE_PROGRAM="/usr/local/bin/ninja"
