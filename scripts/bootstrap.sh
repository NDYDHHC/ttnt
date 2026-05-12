#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"

cd "$repo_root"
git submodule sync --recursive
git submodule update --init

echo "ttnt-workspace top-level submodules are ready"
echo "bootstrap nested dependencies inside each child repo as needed"