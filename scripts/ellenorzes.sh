#!/bin/sh
# Egy parancs: tesztek és tiltólista. Commit és kiadás előtt futtasd.
set -e
cd "$(dirname "$0")/.."
python3 -m unittest
python3 scripts/tiltolista.py
echo "ellenorzes: rendben"
