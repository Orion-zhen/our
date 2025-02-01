#!/bin/bash

shopt -s nullglob
files=(x86_64/*.pkg.tar.zst)

if [[ ${#files[@]} -eq 0 ]]; then
    echo "ERROR: no .pkg.tar.zst files in x86_64!"
    exit 1
fi

file="${files[0]}"
filename=$(basename "$file")

size_bytes=$(stat -c '%s' "$file" 2>/dev/null)

size_mib=$(awk "BEGIN { printf \"%.2f\", $size_bytes / 1024 / 1024 }")

echo "$filename: $size_mib MiB"
