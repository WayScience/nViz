#! /bin/bash

# This script is used to test the configuration of the Linux system.
# We referenced the following to help with configuration:
# https://github.com/pyvista/setup-headless-display-action/blob/v3/action.yml

# One way to run this script through a non-Linux or "clean" environment
# is through Docker. For example:
# docker run --rm -it --platform linux/amd64 -w /app -v $PWD:/app python:3.11 /bin/bash

# install dependencies
apt update
apt-get install -y \
          libglx-mesa0 \
          libgl1 \
          xvfb \
          x11-xserver-utils \
          herbstluftwm \
          libdbus-1-3 \
          libegl1 \
          libopengl0 \
          libosmesa6 \
          libxcb-cursor0 \
          libxcb-icccm4 \
          libxcb-image0 \
          libxcb-keysyms1 \
          libxcb-randr0 \
          libxcb-render-util0 \
          libxcb-shape0 \
          libxcb-xfixes0 \
          libxcb-xinerama0 \
          libxcb-xinput0 \
          libxkbcommon-x11-0 \
          mesa-utils \
          x11-utils

# Set up the display
export DISPLAY=:99.0
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
sleep 3

# Start the window manager
herbstluftwm &
sleep 3

# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# shellcheck disable=SC1091
source "$HOME/.local/bin/env"

# install pre-commit
pip install pre-commit

# install pre-commit hooks
pre-commit install-hooks
