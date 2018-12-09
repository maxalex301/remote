FROM gcc-clang:latest
LABEL maintainer="maxalex"

COPY entrypoint.sh /root/entrypoint.sh
RUN apt update -qq \
  && apt install ${apt_flags} distcc \
  && rm -rf /var/lib/apt/lists \
  && chmod +x /root/entrypoint.sh

EXPOSE 3692

ENTRYPOINT ["/root/entrypoint.sh"]