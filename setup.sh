#!/bin/bash
# Reinstall everything needed to make the films (run: bash setup.sh)
set -e
cd "$(dirname "$0")"
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3 python3-venv ffmpeg libegl1 libgl1 fontconfig fonts-dejavu-core fonts-montserrat fonts-comic-neue fonts-lato fonts-roboto-slab fonts-courier-prime espeak-ng
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
.venv/bin/python -c "import skia, numpy, scipy; print('All set!')"
