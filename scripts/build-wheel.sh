#!/usr/bin/env bash
# Build the LoopX wheel locally, offline.
#
# This is one of the two supported install paths (the other is the in-place
# editable checkout). The wheel is built here and copied to the target machine;
# nothing is fetched from an index. See docs/product/wheel-install.md.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python_bin="${PYTHON:-python3}"
out_dir="dist"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --out-dir)
      out_dir="${2:?--out-dir needs a directory}"
      shift 2
      ;;
    --out-dir=*)
      out_dir="${1#--out-dir=}"
      shift
      ;;
    *)
      echo "build-wheel: unknown argument: $1" >&2
      exit 2
      ;;
  esac
done
mkdir -p "$out_dir"

# 1. Version identity: pyproject.toml and loopx/__init__.py must agree, and the
#    derived tag must be well formed. Exits non-zero on any mismatch.
"$python_bin" scripts/release_artifacts.py expected-tag >/dev/null

# 2. setuptools reuses an existing build/lib tree. A stale one silently ships old
#    or missing files, which is exactly how packaging gaps hide, so always start clean.
rm -rf build/

# 3. Build offline. --no-build-isolation uses the interpreter's own setuptools
#    instead of installing the pinned build requirement from an index.
"$python_bin" -m pip wheel . --no-deps --no-build-isolation --wheel-dir "$out_dir"

version="$("$python_bin" -c 'import loopx; print(loopx.__version__)')"
wheel="$out_dir/loopx-${version}-py3-none-any.whl"
if [ ! -f "$wheel" ]; then
  echo "build-wheel: expected artifact not found: $wheel" >&2
  exit 1
fi

echo "build-wheel: $wheel"
