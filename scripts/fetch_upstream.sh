#!/bin/sh
set -eu

url="https://github.com/yoheinakajima/shared-discovery-paradox.git"
target=".cache/upstream/shared-discovery-paradox"

if [ -d "$target/.git" ]; then
  git -C "$target" fetch --prune origin
else
  mkdir -p .cache/upstream
  git clone --filter=blob:none "$url" "$target"
fi
git -C "$target" rev-parse HEAD
