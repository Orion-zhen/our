#!/bin/bash

export ROOT_DIR=$(pwd)
export REPO=$1

if ! test -f "$ROOT_DIR/$REPO/PKGBUILD"; then
    git clone "https://aur.archlinux.org/${repo}.git"
fi
cd "$ROOT_DIR/$REPO"

if command -v yay &> /dev/null; then
    yay -S --noconfirm $(grep -Po '(?<=^depends=\().*?(?=\))' PKGBUILD | tr -d "'")
    yay -S --noconfirm $(grep -Po '(?<=^makedepends=\().*?(?=\))' PKGBUILD | tr -d "'")
fi

makepkg -scfL --noconfirm --noprogressbar --sign --key $GPG_SIG_KEY --skippgpcheck
rm -rf *-debug-*

if ! mv "$ROOT_DIR/$REPO/"*.pkg.tar.zst* $ROOT_DIR/ 2>/dev/null; then
    echo "Package not found: $REPO"
    exit 1
fi

cd "$ROOT_DIR"
rm -rf $ROOT_DIR/$REPO
