#!/bin/bash
set -e

# ==============================
# 1. 基础环境准备 (所有情况通用)
# ==============================
echo "================================================="
echo ">> [1/5] Preparing base environment..."

# 移除 pacman.conf 中的 VerbosePkgLists 以减少日志噪音
sed -i '/VerbosePkgLists/d' /etc/pacman.conf

# 安装基础依赖
# 注意：先刷新 keys 和系统，确保环境是最新的
pacman -Syu --noconfirm --overwrite '*' base-devel git pacman-contrib mold python-pyyaml sudo tree

# patch makepkg 允许 root 运行 (虽然我们在下面会创建 builder 用户，但这一步通常是为了兼容性或特殊操作)
sed -i '/E_ROOT/d' /usr/bin/makepkg

# ==============================
# 2. 配置 makepkg.conf (核心逻辑)
# ==============================
echo "================================================="
echo ">> [2/5] Configuring makepkg..."
echo "   INPUT_LTO: ${INPUT_LTO}"
echo "   INPUT_CLEAN_BUILD: ${INPUT_CLEAN_BUILD}"

if [ "$INPUT_CLEAN_BUILD" == "true" ]; then
    echo ">> Mode: Clean Build. Using default Arch Linux makepkg.conf."
    # Clean build 不合并任何自定义配置，保持原样

elif [ "$INPUT_LTO" == "true" ]; then
    echo ">> Mode: LTO Enabled. Merging configs/makepkg.conf..."
    if [ -f "./configs/makepkg.conf" ]; then
        cat ./configs/makepkg.conf >> /etc/makepkg.conf
    else
        echo "!! Warning: ./configs/makepkg.conf not found!"
    fi

else
    echo ">> Mode: LTO Disabled. Merging configs/makepkg-no-lto.conf..."
    if [ -f "./configs/makepkg-no-lto.conf" ]; then
        cat ./configs/makepkg-no-lto.conf >> /etc/makepkg.conf
    else
        echo "!! Warning: ./configs/makepkg-no-lto.conf not found!"
    fi
fi

# ==============================
# 3. 设置构建用户
# ==============================
echo "================================================="
echo ">> [3/5] Setting up builder user..."
useradd -m builder
echo "builder ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
chown -R builder:builder .

# 创建 yay 缓存目录
mkdir -p /var/cache/makepkg
chown -R builder:builder /var/cache/makepkg

# ==============================
# 4. 安装 yay
# ==============================
echo "================================================="
echo ">> [4/5] Installing yay..."
git clone --depth 1 https://aur.archlinux.org/yay-bin.git
chown -R builder:builder yay-bin
cd yay-bin
su builder -c "makepkg -si --noconfirm --noprogressbar"
cd ..
rm -rf yay-bin
# 清除 yay 的缓存包，防止混淆
rm -rf /var/cache/makepkg/pkg

# ==============================
# 5. 构建目标包
# ==============================
# $1 是从命令行传入的第一个参数 (即 package name)
echo "================================================="
PACKAGE_NAME="$1"
echo ">> [5/5] Building package: ${PACKAGE_NAME}..."

# 调用 build-one.sh
# 确保传递 HOME 变量，否则 yay/makepkg 可能会找不到用户目录
if [ -f "scripts/build-one.sh" ]; then
    sudo -E -u builder HOME=/home/builder bash scripts/build-one.sh "${PACKAGE_NAME}"
else
    echo "!! Error: scripts/build-one.sh not found!"
    exit 1
fi

# ==============================
# 6. 后处理
# ==============================
# 处理非法文件名 (冒号转下划线)
find . -maxdepth 1 -type f -name '*:*' | while IFS= read -r file; do mv "$file" "${file//:/_}"; done

echo "================================================="
echo ">> Entrypoint finished successfully."
