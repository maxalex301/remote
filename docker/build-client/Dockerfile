FROM clang-base:latest
LABEL maintainer="maxalex"

ARG cmake_version=3.13.1
ARG ninja_version=1.8.2

# Copy public ssh-keys
COPY entrypoint.sh /root/entrypoint.sh

# Install packages
RUN apt install -y  --no-install-recommends --no-install-suggests unzip ca-certificates distcc openssh-server python3-pip python3-setuptools rsync \
    && apt clean \
    && rm -rf /var/lib/apt/lists

# Install build tools: cmake, ninja, conan
RUN curl -SL https://github.com/Kitware/CMake/releases/download/v${cmake_version}/cmake-${cmake_version}-Linux-x86_64.tar.gz | tar -xzC /usr --strip-components=1 \
    && curl -L -o /tmp/ninja-linux.zip https://github.com/ninja-build/ninja/releases/download/v${ninja_version}/ninja-linux.zip \
    && unzip /tmp/ninja-linux.zip -d /usr/bin \
    && rm -f /tmp/ninja-linux.zip \
    && pip3 install --upgrade pip \
    && pip install conan

# Configure SSH
RUN mkdir -p /root/.ssh \
    && mkdir -p /var/run/sshd \
    && chmod -0700 /root/.ssh \
    && chmod +x /root/entrypoint.sh

# Configure Conan
RUN conan profile new --detect default \
    && conan profile update env.CC=/usr/bin/clang default \
    && conan profile update env.CXX=/usr/bin/clang++ default \
    && conan profile update settings.build_type=Release default \
    && conan profile update settings.cppstd=17 default

# Environment variables
ENV CONAN_CMAKE_GENERATOR="Ninja" \
    CONAN_CPU_COUNT=2 \
    CONAN_MAKE_PROGRAM="/usr/bin/ninja"

EXPOSE 22

ENTRYPOINT ["/root/entrypoint.sh"]