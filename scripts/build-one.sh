#!/bin/bash

# 如果任何命令失败，则立即退出脚本，这有助于快速发现错误。
set -e

# 检查是否提供了至少一个包名作为参数。
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <package1> [package2] ..."
    exit 1
fi

# 保存当前工作目录，所有构建产物最终都会被移动到这里。
ROOT_DIR=$(pwd)
echo "Root directory set to: $ROOT_DIR"
echo "Packages to build: $@"
echo # 添加一个空行以提高可读性

# --- 核心构建循环 ---
# 使用 for 循环遍历所有传递给脚本的参数 ("$@")。
# "$@" 会将每个参数作为一个独立的字符串处理，即使参数名中包含空格。
for REPO in "$@"; do
    echo "================================================="
    echo "Processing package: $REPO"
    echo "================================================="

    WORK_DIR="" # 重置工作目录变量

    # 判断是使用本地的 PKGBUILD 还是从 AUR 克隆
    # 1. 使用本地的 PKGBUILD, 则复制一份出来, 使用 makepkg 构建, 然后直接移动产物
    if [ -d "$ROOT_DIR/ourpkg/$REPO" ]; then
        echo "--> Found local package definition for '$REPO'. Using it."
        # 对于本地包，我们复制一份出来进行构建，避免污染源目录
        cp -r "$ROOT_DIR/ourpkg/$REPO" .
        WORK_DIR="$ROOT_DIR/$REPO"

        # 进入构建目录
        cd "$WORK_DIR"

        # --- 构建包 ---
        # -f/--force: 即使包已经存在，也强制重新构建。
        # -c/--clean: 构建完成后清理工作目录（删除 $srcdir）。
        # -L/--log: 将构建过程记录到日志文件，方便调试。
        # --sign: 使用 GPG_SIG_KEY 环境变量中指定的密钥进行签名。
        # --skippgpcheck: 跳过对源文件 PGP 签名的验证（在受控的 CI 环境中通常是安全的）。
        echo "--> Building package '$REPO'..."
        makepkg -fcL --noconfirm --noprogressbar

        echo "--> Moving built packages to root directory..."
        # 对于 makepkg 构建的包
        # 使用 find 来移动构建好的包和签名文件，比 'mv' 通配符更安全。
        # 如果找不到文件，find 不会报错退出，所以我们后面需要检查。
        find . -maxdepth 1 -name "*.pkg.tar.zst*" -exec mv {} "$ROOT_DIR/" \;

        cd "$ROOT_DIR"

        # 清理构建目录
        echo "--> Cleaning up work directory for '$REPO'."
        rm -rf "$WORK_DIR"

    else
        if [ -n "$INPUT_BASE" ]; then
            echo "--> Base package specified. Fetching PKGBUILD for '$INPUT_BASE' from AUR."
            git clone --depth 1 "https://aur.archlinux.org/$INPUT_BASE.git"
            
            WORK_DIR="$ROOT_DIR/$INPUT_BASE"
            cd "$WORK_DIR"
            
            echo "--> Patching pkgname in PKGBUILD to '$REPO'..."
            echo "" >> PKGBUILD
            echo "pkgname=\"$REPO\"" >> PKGBUILD
            echo "provides+=(\"$INPUT_BASE\")" >> PKGBUILD
            echo "conflicts+=(\"$INPUT_BASE\")" >> PKGBUILD

            # 由于 makepkg -s 只能通过 pacman 安装官方源依赖，不能自动从 AUR 拉取
            # 我们先提炼出新包的依赖，然后用 yay 把它们准备好
            echo "--> Pre-installing AUR dependencies via yay..."
            # 源中依赖通过 makepkg -s 安装，AUR 依赖如果此时没装，makepkg 会报错，不如直接让 yay 扫一遍该目录的依赖安装
            # makepkg --printsrcinfo 可用于提取依赖, 但直接用 yay --builddir 下载构建更稳妥，或者利用 makepkg -s --syncdeps 的机制
            # 其实最简单的是直接从 PKGBUILD 提取依赖调用 yay 安装：
            source PKGBUILD
            if [ -n "${depends[*]}" ] || [ -n "${makedepends[*]}" ]; then
                yay -S --noconfirm --needed "${depends[@]}" "${makedepends[@]}" 2>/dev/null || true
            fi

            echo "--> Building patched package '$REPO'..."
            # --syncdeps (-s) is used to install standard repo missing dependencies
            makepkg -sfcL --noconfirm --noprogressbar

            echo "--> Moving built patched packages to root directory..."
            # For makepkg, it goes to PKGDEST and/or current dir. Check both.
            find . -maxdepth 1 -name "*.pkg.tar.zst*" -exec mv {} "$ROOT_DIR/" \; 2>/dev/null || true
            find "/var/cache/makepkg/pkg" -name "${REPO}*.pkg.tar.zst*" -exec mv {} "$ROOT_DIR/" \; 2>/dev/null || true

            cd "$ROOT_DIR"
            rm -rf "$WORK_DIR"
        else
            echo "--> No local package found. Building '$REPO' from AUR."
            yay -S --noconfirm --noprogressbar --overwrite '*' "$REPO"
        fi

        echo "--> Moving built packages to root directory..."
        # 2. 使用 yay 构建的包
        # 构建结果放在 `configs/makepkg.conf` 中 `PKGDEST` 变量的目录中
        # 被配置为 `/var/cache/makepkg/pkg`
        read -r -a EXCLUDES_ARRAY <<< "$INPUT_EXCLUDE"
        for foreign in $(pacman -Qmq); do
            skip=false
            for e in "${EXCLUDES_ARRAY[@]}"; do
                if [ "$foreign" == "$e" ]; then
                    echo "--> Skipping excluded package: '$foreign'"
                    skip=true
                    break
                fi
            done
            if [ "$skip" == "true" ]; then continue; fi

            find "/var/cache/makepkg/pkg" -name "${foreign}*" -exec mv {} "$ROOT_DIR/" \;
        done

        cd "$ROOT_DIR"
    fi

    # 回到根目录，准备处理下一个包
    cd "$ROOT_DIR"

    # 检查是否真的有包被移动了过来
    # `ls` 的结果通过 `wc -l` 计数，如果不为 0，说明成功了
    if [ $(ls -1 ${REPO}*.pkg.tar.zst 2>/dev/null | wc -l) -eq 0 ]; then
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo "!!! Critical Error: Build for '$REPO' did not produce any package files."
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        exit 1
    fi

    echo "--- Successfully processed package: $REPO ---"
    echo # 添加一个空行以提高可读性

done

echo "================================================="
echo "All packages built successfully!"
echo "Final packages in root directory:"
ls -l *.pkg.tar.zst*
echo "================================================="