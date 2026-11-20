#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

python3 -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

pyinstaller --noconfirm --clean \
  --name berlip_MS \
  --windowed \
  --onefile \
  main.py

echo "Build finished. Binary at dist/berlip_MS"
