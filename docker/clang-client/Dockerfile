FROM clang-cmake-conan:latest
LABEL maintainer="maxalex"

# Copy public ssh-keys
COPY entrypoint.sh /root/entrypoint.sh

# Install packages
RUN apt update -qq \
    && apt install ${apt_flags} openssh-server rsync \
    && apt clean \
    && rm -rf /var/lib/apt/lists \
    && mkdir -p /root/.ssh \
    && mkdir -p /var/run/sshd \
    && chmod -0700 /root/.ssh \
    && chmod +x /root/entrypoint.sh

EXPOSE 22

ENTRYPOINT ["/root/entrypoint.sh"]