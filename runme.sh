#!/bin/bash

# Root-check
if [[ $EUID -eq 0 ]]; then
  echo "Do not run as root" 2>&1
  exit 1
fi

echo "Generating Image"
./generate.py
echo "Displaying Image"
./display.py data/display.png
