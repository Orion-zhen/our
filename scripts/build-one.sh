#!/bin/bash

export ROOT_DIR=$(pwd)
export REPO=$1

if test -f "$ROOT_DIR/ourpkg/$REPO/PKGBUILD"; then
    export WORK_DIR="$ROOT_DIR/ourpkg/$REPO"
else
    git clone "https://aur.archlinux.org/$REPO.git"
    export WORK_DIR="$ROOT_DIR/$REPO"
fi
cd "$WORK_DIR"

if command -v yay &>/dev/null; then
    yay -S --noconfirm $(grep -Po '(?<=^depends=\().*?(?=\))' PKGBUILD | tr -d "'")
    yay -S --noconfirm $(grep -Po '(?<=^makedepends=\().*?(?=\))' PKGBUILD | tr -d "'")
fi

makepkg -scfL --noconfirm --noprogressbar --sign --key $GPG_SIG_KEY --skippgpcheck
rm -rf *-debug-*

if ! mv $WORK_DIR/*.pkg.tar.zst* $ROOT_DIR/ 2>/dev/null; then
    echo "Package not found: $REPO"
    exit 1
fi

cd "$ROOT_DIR"
rm -rf "$WORK_DIR"
