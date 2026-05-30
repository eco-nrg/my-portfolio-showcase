FROM debian:bookworm-slim

ENV HOME=/root
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    build-essential \
    fluxbox \
    git \
    net-tools \
    novnc \
    supervisor \
    x11vnc \
    xterm \
    xvfb \
    curl \
    gpg \ 
    python3 \
    python3-pip \
    python3-pyqt5 \
    python3-pyqt5.qtquick \
    python3-pyqt5.qtsvg \
    python-is-python3 \
    qml-module-qtquick2 \
    qml-module-qtquick-controls2 \
    qml-module-qtquick-layouts \
    qml-module-qtquick-templates2 \
    qml-module-qtquick-window2 \
    qml-module-qt-labs-qmlmodels \
    # Cleaning cache:
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

RUN cp /usr/share/novnc/vnc.html /usr/share/novnc/index.html

WORKDIR /app

RUN pip install --break-system-packages \
    redis==4.5.5 \
    qrcode==7.4.2 \
    Pillow==9.4.0 \
    pydantic==1.9.1 \
    rich==13.4 \
    structlog==23.1 \
    structlog-sentry==2.0.3 \
    requests==2.25.1

COPY ./fake-pi /app

COPY ./py_scripts /app/py_scripts
COPY ./kv /app/kv
COPY ./pyqt /app/pyqt

ENV DISPLAY=:0.0
ENV DISPLAY_WIDTH=800
ENV DISPLAY_HEIGHT=600
ENV RUN_XTERM=no
ENV RUN_FLUXBOX=no

CMD ["/app/entrypoint.sh"]
EXPOSE 8080