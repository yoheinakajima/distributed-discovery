#!/bin/sh
set -eu
selection="${1:-all}"
echo "paper source validation requested: $selection"
echo "paper builds are registered for M3/M5/M6; no buildable LaTeX source exists yet" >&2
exit 3
