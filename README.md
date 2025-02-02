# OUR

Orion User's Repository for Arch Linux

This repository includes a bunch of useful AUR packages that are not listed in other popular Arch repositories, such as linuxqq, wechat, wemeet, dingtalk, watt-toolkit(i.e. steam++), etc.

The repository builder is powered by GitHub Actions. It will automatically pull AUR packages, build them, and release to my GitHub page and Huggingface repository everyday 😉

If you want some nice packages in AUR, just feel free to issue 🤗

## Features

- [x] Use hierarchical build steps to resolve dependencies between AUR packages
- [x] Provides a variety of useful AUR packages:
  - [x] Social Apps: [linuxqq](https://aur.archlinux.org/packages/linuxqq), [wechat](https://aur.archlinux.org/packages/wechat), [wemeet-bin](https://aur.archlinux.org/packages/wemeet-bin), [dingtalk-bin](https://aur.archlinux.org/packages/dingtalk-bin), etc.
  - [x] Media Apps: [bilibili](https://aur.archlinux.org/packages/bilibili), [yesplaymusic-plus](https://aur.archlinux.org/packages/yesplaymusic-plus), [listen1](https://aur.archlinux.org/packages/listen1), [4kvideodownloaderplus](https://aur.archlinux.org/packages/4kvideodownloaderplus), etc.
  - [x] Proxy tools: [mihomo](https://aur.archlinux.org/packages/mihomo), [hiddify](https://aur.archlinux.org/packages/hiddify), [watt-toolkit-bin](https://aur.archlinux.org/packages/watt-toolkit-bin), etc.
  - [x] Powerful Apps: [vmware-workstation](https://aur.archlinux.org/packages/vmware-workstation), [chatbox-bin](https://aur.archlinux.org/packages/chatbox-bin), etc.
  - [x] And more to discover...
- [x] Signed with my GPG key
- [x] Built and released everyday to ensure the latest packages
- [x] Backup sources on Huggingface and HF-Mirror
- [x] Completely **FREE** to community with GPL-v3.0 license

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
