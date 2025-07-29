ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install headless‐display, OpenGL bits, git, and fontconfig for VisPy
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      xvfb \
      libgl1-mesa-glx \
      libgl1-mesa-dri \
      libosmesa6-dev \
      libxrender1 \
      libxext6 \
      fontconfig \
      git \
 && rm -rf /var/lib/apt/lists/*

# non‑root user
RUN useradd --create-home appuser
USER appuser
WORKDIR /home/appuser

# mount point for your code
RUN mkdir -p /home/appuser/app
VOLUME ["/home/appuser/app"]

# on start, fire up Xvfb then exec your CMD (or bash)
ENTRYPOINT ["sh","-c","Xvfb :99 -screen 0 1024x768x24 & export DISPLAY=:99 && exec \"${@:-bash}\"","--"]
CMD []
