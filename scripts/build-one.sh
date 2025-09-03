#!/bin/bash

# 如果任何命令失败，则立即退出脚本，这有助于快速发现错误。
set -e

# --- 全局设置 ---
# 如果 GPG_SIGN 变量未设置, 或者其值不为 "0" 或 "false", 则执行签名校验
if [ -z "$GPG_SIGN" ] || { [ "$GPG_SIGN" != "0" ] && [ "${GPG_SIGN,,}" != "false" ]; }; then
    # 检查 GPG 签名密钥是否已设置，这是构建的关键
    if [ -z "$GPG_SIG_KEY" ]; then
        echo "Error: GPG_SIG_KEY environment variable is not set."
        exit 1
    fi
fi

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
    if [ -d "$ROOT_DIR/ourpkg/$REPO" ]; then
        echo "--> Found local package definition for '$REPO'. Using it."
        # 对于本地包，我们复制一份出来进行构建，避免污染源目录
        cp -r "$ROOT_DIR/ourpkg/$REPO" .
        WORK_DIR="$ROOT_DIR/$REPO"
    else
        echo "--> No local package found. Cloning '$REPO' from AUR."
        git clone "https://aur.archlinux.org/$REPO.git"
        WORK_DIR="$ROOT_DIR/$REPO"
    fi

    # 进入构建目录
    cd "$WORK_DIR"

    # --- 依赖安装 ---
    # 使用 makepkg 自身的功能来处理依赖，这是更标准、更可靠的做法。
    # -s/--syncdeps: 会自动同步并安装 `depends` 和 `makedepends` 中缺失的依赖。
    # --noconfirm: 避免在安装依赖时需要手动确认。
    echo "--> Syncing dependencies for '$REPO'..."
    if command -v yay &>/dev/null; then
        echo "--> Using yay for dependency sync."
        yay -S --noconfirm --overwrite '*' "$REPO"
    else
        echo "--> Using pacman for dependency sync."
        makepkg --syncdeps --noconfirm --noprogressbar
    fi

    # --- 构建包 ---
    # -f/--force: 即使包已经存在，也强制重新构建。
    # -c/--clean: 构建完成后清理工作目录（删除 $srcdir）。
    # -L/--log: 将构建过程记录到日志文件，方便调试。
    # --sign: 使用 GPG_SIG_KEY 环境变量中指定的密钥进行签名。
    # --skippgpcheck: 跳过对源文件 PGP 签名的验证（在受控的 CI 环境中通常是安全的）。
    echo "--> Building package '$REPO'..."
    # 如果 GPG_SIGN 变量未设置, 或者其值不为 "0" 或 "false", 则执行签名操作
    if [ -z "$GPG_SIGN" ] || { [ "$GPG_SIGN" != "0" ] && [ "${GPG_SIGN,,}" != "false" ]; }; then
        makepkg -fcL --noconfirm --noprogressbar --sign --key "$GPG_SIG_KEY" --skippgpcheck
    else
        makepkg -fcL --noconfirm --noprogressbar
    fi

    # --- 清理和移动产物 ---
    # 删除调试包（如果生成了的话）
    # rm -f *-debug-*.pkg.tar.zst*

    echo "--> Moving built packages to root directory..."
    # 使用 find 来移动构建好的包和签名文件，比 'mv' 通配符更安全。
    # 如果找不到文件，find 不会报错退出，所以我们后面需要检查。
    find . -maxdepth 1 -name "*.pkg.tar.zst*" -exec mv {} "$ROOT_DIR/" \;

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

    # 清理构建目录
    echo "--> Cleaning up work directory for '$REPO'."
    rm -rf "$WORK_DIR"

    echo "--- Successfully processed package: $REPO ---"
    echo # 添加一个空行以提高可读性

done

echo "================================================="
echo "All packages built successfully!"
echo "Final packages in root directory:"
ls -l *.pkg.tar.zst*
echo "================================================="