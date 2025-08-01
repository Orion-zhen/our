# OUR

Orion User's Repository for Arch Linux

This repository includes a bunch of useful AUR packages that are not listed in other popular Arch repositories, such as linuxqq, wechat, wemeet, dingtalk, watt-toolkit(i.e. steam++), etc.

The repository builder is powered by GitHub Actions. It will automatically pull AUR packages, build them, and release to my GitHub page and Huggingface repository everyday 😉

If you want some nice packages in AUR, just feel free to issue 🤗

## Features

- ✅ Use hierarchical build steps to resolve dependencies between AUR packages
- ✅ Provides a variety of useful AUR packages
- ✅ Signed with my GPG key
- ✅ Built and released everyday to ensure the latest packages
- ✅ Backup sources on Huggingface and HF-Mirror
- ✅ Completely **FREE** to community with GPL-v3.0 license

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

## Development

If you want to build your own repository, just fork this repository, and add these secrets to your Actions environment:

- `GPG_SEC_KEY`: Your GPG secret key
- `GPG_SIG_KEY`: Your GPG key used for signatures
- `GPG_PASSPHRASE`: Your GPG key password
- `AUR_SSH_PRIVATE_KEY`: Your SSH key used for AUR

## Credits

This repository is inspired by [LeonidPilyugin/kawaii-repo](https://github.com/LeonidPilyugin/kawaii-repo), which contains a bunch of small packages and is maintained on GitHub.
