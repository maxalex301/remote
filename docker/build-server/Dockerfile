FROM maxalex/gcc-clang:latest
LABEL maintainer="maxalex"

COPY entrypoint.sh /entrypoint.sh
RUN apt update -qq \
  && apt install ${apt_flags} distcc \
  && rm -rf /var/lib/apt/lists \
  && chmod 755 /entrypoint.sh

EXPOSE 3692

ENTRYPOINT ["/entrypoint.sh"]
