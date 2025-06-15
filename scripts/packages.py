import os
import json
import tarfile
import zstandard

# --- 配置 ---
PKG_DIR = "x86_64"
OUTPUT_FILE = "packages.json"
PKG_SUFFIX = ".pkg.tar.zst"


def parse_pkginfo(pkg_path):
    """
    从 .pkg.tar.zst 文件中读取 .PKGINFO 并解析元数据。
    这是最可靠的方法。
    """
    metadata = {}
    try:
        with open(pkg_path, "rb") as f:
            dctx = zstandard.ZstdDecompressor()
            # 使用流式读取，避免将整个文件解压到内存
            with dctx.stream_reader(f) as reader:
                with tarfile.open(fileobj=reader, mode="r|") as tar:
                    for member in tar:
                        if member.name == ".PKGINFO":
                            # 提取 .PKGINFO 文件内容
                            pkginfo_file = tar.extractfile(member)
                            if pkginfo_file:
                                content = pkginfo_file.read().decode("utf-8")
                                # 解析 .PKGINFO 的键值对
                                for line in content.splitlines():
                                    if " = " in line:
                                        key, value = line.split(" = ", 1)
                                        metadata[key.strip()] = value.strip()
                            # 找到后即可退出循环
                            break
    except Exception as e:
        print(f"Error processing file '{os.path.basename(pkg_path)}': {e}")
        return None

    # 我们只需要包名和版本
    if "pkgname" in metadata and "pkgver" in metadata:
        return {
            "name": metadata["pkgname"],
            "version": metadata["pkgver"],
            "arch": metadata.get("arch", "unknown"),  # .PKGINFO 中也有 arch
        }
    return None


def main():
    """
    主函数，执行所有操作。
    """
    print(f"Starting robust package scan in './{PKG_DIR}'...")

    if not os.path.isdir(PKG_DIR):
        print(f"Error: Directory '{PKG_DIR}' not found.")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return

    packages_list = []

    for filename in os.listdir(PKG_DIR):
        if not filename.endswith(PKG_SUFFIX):
            continue

        file_path = os.path.join(PKG_DIR, filename)

        # 1. 从包内部解析元数据
        pkg_info = parse_pkginfo(file_path)

        if not pkg_info:
            print(f"Warning: Could not parse metadata from '{filename}'. Skipping.")
            continue

        # 2. 获取文件大小
        try:
            file_size_bytes = os.path.getsize(file_path)
        except FileNotFoundError:
            print(f"Warning: Could not find file '{file_path}' to get size. Skipping.")
            continue

        # 3. 组织数据
        packages_list.append(
            {
                "name": pkg_info["name"],
                "version": pkg_info["version"],
                "arch": pkg_info["arch"],
                "size": file_size_bytes,
                "filename": filename,
            }
        )

    # 按软件包名称字母顺序排序
    packages_list.sort(key=lambda p: p["name"].lower())

    # 4. 生成 JSON 文件
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(packages_list, f, indent=2, ensure_ascii=False)
        print(f"\nSuccess! Found and processed {len(packages_list)} packages.")
        print(f"Package data has been written to '{OUTPUT_FILE}'.")
    except IOError as e:
        print(f"Error writing to file '{OUTPUT_FILE}': {e}")


if __name__ == "__main__":
    main()
