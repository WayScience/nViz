# referenced with modifications from
# https://github.com/napari/napari/blob/main/dockerfile
FROM --platform=linux/amd64 python:3.11 AS napari

# below env var required to install libglib2.0-0 non-interactively
ENV TZ=America/Los_Angeles
ARG DEBIAN_FRONTEND=noninteractive
ARG NAPARI_COMMIT=main

WORKDIR /nviz

# install python resources + graphical libraries used by qt and vispy
RUN apt-get update && \
    apt-get install -qqy  \
        build-essential \
        git \
        mesa-utils \
        x11-utils \
        libegl1-mesa \
        libopengl0 \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libfontconfig1 \
        libxrender1 \
        libdbus-1-3 \
        libxkbcommon-x11-0 \
        libxi6 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-render-util0 \
        libxcb-xinerama0 \
        libxcb-xinput0 \
        libxcb-xfixes0 \
        libxcb-shape0 \
        && apt-get clean

# install napari from repo
# see https://github.com/pypa/pip/issues/6548#issuecomment-498615461 for syntax
RUN pip install --upgrade pip

ENTRYPOINT ["/bin/bash"]
