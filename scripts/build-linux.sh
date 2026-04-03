#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python -m pip install --upgrade pip
pip install -r requirements-dev.txt

rm -rf build-pyinstaller dist-bin

pyinstaller \
  --noconfirm \
  --clean \
  --onefile \
  --name copyast \
  --paths src \
  --distpath dist-bin \
  --workpath build-pyinstaller \
  src/app/main.py

echo "Build completed: dist-bin/copyast"