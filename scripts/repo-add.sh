#!/bin/bash

export ROOT_DIR=$(pwd)
export REPO_NAME="${1:-our}"

mkdir -p $ROOT_DIR/x86_64
cd $ROOT_DIR/x86_64

# 如果 GPG_SIGN 变量未设置, 或者其值不为 "0" 或 "false", 则执行签名操作
if [ -z "$GPG_SIGN" ] || { [ "$GPG_SIGN" != "0" ] && [ "${GPG_SIGN,,}" != "false" ]; }; then
    echo "==> GPG_SIGN is enabled. Signing the repository..."
    # 添加软件包到仓库数据库, 并进行 GPG 签名
    repo-add --verify --sign --key "$GPG_SIG_KEY" "$REPO_NAME.db.tar.gz" *.pkg.tar.zst

    # 清理旧的数据库和文件列表符号链接 (如果存在)
    rm -f "$REPO_NAME.db" "$REPO_NAME.db.sig" "$REPO_NAME.files" "$REPO_NAME.files.sig"

    # 复制新的数据库和文件列表, 包括签名文件
    cp "$REPO_NAME.db.tar.gz" "$REPO_NAME.db"
    cp "$REPO_NAME.db.tar.gz.sig" "$REPO_NAME.db.sig"
    cp "$REPO_NAME.files.tar.gz" "$REPO_NAME.files"
    cp "$REPO_NAME.files.tar.gz.sig" "$REPO_NAME.files.sig"
else
    echo "==> GPG_SIGN is disabled. Skipping repository signing..."
    # 添加软件包到仓库数据库, 不进行签名
    repo-add --verify "$REPO_NAME.db.tar.gz" *.pkg.tar.zst

    # 清理旧的数据库和文件列表符号链接 (如果存在)
    rm -f "$REPO_NAME.db" "$REPO_NAME.db.sig" "$REPO_NAME.files" "$REPO_NAME.files.sig"

    # 仅复制新的数据库和文件列表 (不含签名)
    cp "$REPO_NAME.db.tar.gz" "$REPO_NAME.db"
    cp "$REPO_NAME.files.tar.gz" "$REPO_NAME.files"
fi
