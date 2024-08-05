FROM archlinux:latest

RUN pacman -Syu --noconfirm --noprogressbar && pacman --noconfirm --noprogressbar -S sox expect cmake base-devel python-pip python python-requests fftw openbsd-netcat git
RUN mkdir /eas-notifier && chown 1001:1001 /eas-notifier
WORKDIR /eas-notifier
ADD scripts /eas-notifier/scripts
RUN bash /eas-notifier/scripts/build_multimon && bash /eas-notifier/scripts/get_dsame3 && useradd -d /eas-notifier -r -u 1001 server
EXPOSE 4898/udp
USER server
# Disable buffering so that we can receive the text from multimon
ENTRYPOINT ["stdbuf", "-i0", "-o0", "-e0", "bash", "/eas-notifier/scripts/run"]
