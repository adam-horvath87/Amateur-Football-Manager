#!/bin/bash
# Foci Manager – Linux indítószkript
cd "$(dirname "$0")"

# Pygame telepítése ha szükséges
python3 -c "import pygame" 2>/dev/null || pip3 install pygame --break-system-packages

python3 main.py
