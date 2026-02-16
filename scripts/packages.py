import os
import json
import tarfile
import zstandard
from collections import defaultdict

# --- 配置 ---
# 如果目录不存在，主程序会尝试搜索当前目录作为备选
PKG_DIR = "x86_64"
OUTPUT_FILE = "packages.json"
PKG_SUFFIX = ".pkg.tar.zst"


def _extract_pkginfo_content(pkg_path):
    """辅助函数：从压缩包中安全提取 .PKGINFO 的原始内容"""
    with open(pkg_path, "rb") as f:
        dctx = zstandard.ZstdDecompressor()
        # 合并上下文管理以减少缩进
        with dctx.stream_reader(f) as reader, tarfile.open(fileobj=reader, mode="r|") as tar:
            for member in tar:
                if member.name != ".PKGINFO":
                    continue
                f_obj = tar.extractfile(member)
                return f_obj.read().decode("utf-8") if f_obj else ""
    return None


def parse_pkginfo(pkg_path):
    """
    解析 .PKGINFO 并提取元数据。使用扁平化逻辑提高可读性。
    """
    try:
        content = _extract_pkginfo_content(pkg_path)
    except Exception as e:
        print(f"Error processing file '{os.path.basename(pkg_path)}': {e}")
        return None

    if content is None:
        return None

    raw = defaultdict(list)
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or " = " not in line:
            continue

        key, value = line.split(" = ", 1)
        raw[key.strip()].append(value.strip())

    # 动态转换：单一值转为标量，多个值保留为列表
    return {k: v[0] if len(v) == 1 else v for k, v in raw.items()}


def main():
    """
    主函数，扫码目录并提取所有包的元数据。
    """
    # 路径检查与备选方案
    search_dir = PKG_DIR
    if not os.path.isdir(search_dir):
        if search_dir == "x86_64" and any(f.endswith(PKG_SUFFIX) for f in os.listdir(".")):
            print(f"Warning: Directory '{PKG_DIR}' not found, but packages found in '.', using current directory.")
            search_dir = "."
        else:
            print(f"Error: Directory '{search_dir}' not found.")
            if not os.path.exists(OUTPUT_FILE):
                os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f)
            return

    print(f"Starting robust package scan in './{search_dir}'...")
    packages_list = []

    for filename in os.listdir(search_dir):
        if not filename.endswith(PKG_SUFFIX):
            continue

        file_path = os.path.join(search_dir, filename)

        # 1. 从包内部解析元数据
        pkg_info = parse_pkginfo(file_path)

        if not pkg_info:
            print(f"Warning: Could not parse metadata from '{filename}'. Skipping.")
            continue

        # 2. 获取文件大小 (压缩后的包大小)
        try:
            file_size_bytes = os.path.getsize(file_path)
        except FileNotFoundError:
            print(f"Warning: Could not find file '{file_path}' to get size. Skipping.")
            continue

        # 3. 组织数据
        # 保证原有输出核心字段不变 (name, version, arch, size, filename)
        entry = {
            "name": pkg_info.get("pkgname", "unknown"),
            "version": pkg_info.get("pkgver", "unknown"),
            "arch": pkg_info.get("arch", "unknown"),
            "size": file_size_bytes,  # 这里的 size 保持为文件压缩大小
            "filename": filename,
        }

        # 提取所有其他可能的元资料
        for key, value in pkg_info.items():
            # 排除已明确映射的字段
            if key in ["pkgname", "pkgver"]:
                continue

            # size 字段在 PKGINFO 中是安装后的解压大小
            # 为避免与外层 'size' 冲突，重命名为 installed_size
            if key == "size":
                try:
                    entry["installed_size"] = int(value)
                except (ValueError, TypeError):
                    entry["installed_size"] = value
            elif key == "builddate":
                try:
                    entry["builddate"] = int(value)
                except (ValueError, TypeError):
                    entry["builddate"] = value
            elif key == "arch":
                # arch 已在 entry 中，确保它是最新的
                entry["arch"] = value
            else:
                # 其他所有字段 (pkgdesc, url, depend 等) 直接加入
                entry[key] = value

        packages_list.append(entry)

    # 按软件包名称字母顺序排序
    packages_list.sort(key=lambda p: p["name"].lower())

    # 4. 生成 JSON 文件
    # 确保目标目录存在
    output_dir = os.path.dirname(OUTPUT_FILE)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(packages_list, f, indent=2, ensure_ascii=False)
        print(f"\nSuccess! Found and processed {len(packages_list)} packages.")
        print(f"Package data has been written to '{OUTPUT_FILE}'.")
    except IOError as e:
        print(f"Error writing to file '{OUTPUT_FILE}': {e}")


if __name__ == "__main__":
    main()
