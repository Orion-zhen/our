---
license: gpl-3.0
tags:
- arch
- archlinux
- AUR
website: https://orion-zhen.github.io/our
---

# OUR

Orion User's Repository for Arch Linux

The repo uses GitHub Actions to auto build some AUR packages and release them to GitHub and Huggingface daily 😉

If you want some nice packages in AUR, just feel free to issue 🤗

## Usage

To use this repository, add it to your `/etc/pacman.conf`:

```text
[our]
Server = https://orion-zhen.github.io/our/$arch
```

Command line:

```shell
sudo tee -a /etc/pacman.conf << EOF
[our]
Server = https://orion-zhen.github.io/our/$arch
EOF
```

OUR repository is ready to use 😃

If you somehow cannot access to the GitHub page, you can download packages from [Huggingface](https://huggingface.co/Orion-zhen/our) or [hf-mirror](https://hf-mirror.com/Orion-zhen/our) and then install them using `pacman -U`.

So you could:

1. search for packages in OUR using `pacman` as normal
2. download some package using `huggingface-cli` if it's in OUR
3. install the package using `pacman -U`

```shell
pacman -Ss <package-name>
huggingface-cli download Orion-zhen/our --local-dir <download-dir> --include "<package-name>-*"
sudo pacman -U <download-dir>/<package-name>-<version>.pkg.tar.zst
```

That's a very tricky way, isn't it? But I don't want to buy any expensive LFS storage space from GitHub, so let's call it a repository 😋

## Credits

This repository is inspired by [LeonidPilyugin/kawaii-repo](https://github.com/LeonidPilyugin/kawaii-repo), which contains a bunch of small packages and is maintained on GitHub.
