#!/usr/bin/env python3

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import requests
import yaml

# --- 全局配置 ---
AUR_API_URL = "https://aur.archlinux.org/rpc.php"
OFFICIAL_API_URL = "https://archlinux.org/packages/search/json/"

HTTP_SESSION = requests.Session()
HTTP_SESSION.headers.update({"User-Agent": "AUR-Dependency-Resolver/3.5-Optimized"})

# --- 性能优化缓存 ---
# 缓存已处理过的包，避免重复构建依赖树
PROCESSED_PACKAGES_CACHE: Dict[str, Dict] = {}
# 缓存官方源的查询结果，避免重复网络请求
OFFICIAL_CACHE: Dict[str, Optional[str]] = {}


class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True


parser = argparse.ArgumentParser(
    description="为 AUR 软件包生成纯 AUR 依赖树，严格优先官方源替代品 (优化版)。"
)
parser.add_argument("package_name", help="要分析其依赖关系的根 AUR 软件包的名称。")
parser.add_argument(
    "--file",
    "-f",
    help="可选: 要读取和更新的 YAML 文件的路径。如果省略，则将结果打印到控制台。",
)
parser.add_argument(
    "--verbose", "-v", action="store_true", default=False, help="打印更多信息。"
)
args = parser.parse_args()
assert isinstance(args.verbose, bool)

# --- API 查询工具函数 ---

def query_aur_info_batch(package_names: List[str]) -> Dict[str, Dict]:
    """(优化) 使用单次请求批量查询 AUR 获取多个软件包的信息"""
    if not package_names:
        return {}
    params = [("v", "5"), ("type", "info")]
    params.extend(("arg[]", name) for name in package_names)
    try:
        response = HTTP_SESSION.get(AUR_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return {pkg["Name"]: pkg for pkg in data.get("results", [])}
    except (requests.RequestException, json.JSONDecodeError):
        return {}


def find_aur_provider(package_name: str) -> Optional[str]:
    """在 AUR 中通过 provides 字段查找软件包"""
    params = {"v": "5", "type": "search", "by": "provides", "arg": package_name}
    try:
        response = HTTP_SESSION.get(AUR_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("resultcount", 0) > 0:
            return data["results"][0]["Name"]
        return None
    except (requests.RequestException, json.JSONDecodeError):
        return None


def find_official_alternative(package_name: str) -> Optional[str]:
    """(优化) 检查官方源中是否有任何包可以替代给定的包名，并缓存结果"""
    if package_name in OFFICIAL_CACHE:
        return OFFICIAL_CACHE[package_name]

    names_to_check = {package_name}
    base_name = re.sub(r"(-git|-bin|-svn|-hg|-bzr|-testing|-debug)$", "", package_name)
    if base_name != package_name:
        names_to_check.add(base_name)

    for name in sorted(list(names_to_check), key=len, reverse=True):
        params = {"q": name}
        try:
            response = HTTP_SESSION.get(OFFICIAL_API_URL, params=params)
            response.raise_for_status()
            results = response.json().get("results", [])
            if not results:
                continue

            for pkg_data in results:
                if pkg_data["pkgname"] == name:
                    OFFICIAL_CACHE[package_name] = pkg_data["pkgname"]
                    return pkg_data["pkgname"]

                provides_list = pkg_data.get("provides", [])
                cleaned_provides = [clean_dependency_name(p) for p in provides_list]
                if name in cleaned_provides:
                    OFFICIAL_CACHE[package_name] = pkg_data["pkgname"]
                    return pkg_data["pkgname"]

                conflicts_list = pkg_data.get("conflicts", [])
                cleaned_conflicts = [clean_dependency_name(c) for c in conflicts_list]
                if name in cleaned_conflicts:
                    OFFICIAL_CACHE[package_name] = pkg_data["pkgname"]
                    return pkg_data["pkgname"]

        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"[-] 在官方源中搜索 '{name}' 时出错: {e}", file=sys.stderr)
            continue
    
    OFFICIAL_CACHE[package_name] = None
    return None


# --- 核心逻辑 ---


def clean_dependency_name(dep: str) -> str:
    """从依赖字符串中移除版本约束"""
    return re.split(r"[<>=]", dep, maxsplit=1)[0].strip()


def build_aur_dependency_tree(package_name: str) -> Optional[Dict[str, Any]]:
    """(优化) 为那些没有官方替代品的 AUR 包构建依赖树"""
    if package_name in PROCESSED_PACKAGES_CACHE:
        return PROCESSED_PACKAGES_CACHE[package_name]

    print(f"\n[->] 正在分析 AUR 包: {package_name}")

    # 初始包信息仍需单独获取
    pkg_info_map = query_aur_info_batch([package_name])
    if package_name not in pkg_info_map:
        print(f"[-] 警告: 在 AUR 中找不到包 '{package_name}'，可能已被移除或重命名。")
        return None
    pkg_info = pkg_info_map[package_name]

    node = {"name": package_name}
    PROCESSED_PACKAGES_CACHE[package_name] = node

    all_deps: Set[str] = set()
    for dep_type in ["Depends", "MakeDepends", "CheckDepends"]:
        all_deps.update(pkg_info.get(dep_type, []))

    if not all_deps:
        if args.verbose:
            print(f"[i] 包 '{package_name}' 没有需要分析的 AUR 依赖。")
        return node

    # --- 优化点: 批量处理依赖 ---
    # 1. 清理并收集所有唯一的依赖名称
    cleaned_deps = {clean_dependency_name(d) for d in all_deps if clean_dependency_name(d)}
    
    # 2. 批量过滤掉在官方源中存在的依赖
    aur_candidates = set()
    for dep in cleaned_deps:
        official_alternative = find_official_alternative(dep) # 使用了缓存
        if official_alternative:
            if args.verbose:
                print(f"[i] 依赖 '{dep}' 由官方包 '{official_alternative}' 满足。跳过。")
        else:
            aur_candidates.add(dep)

    if not aur_candidates:
        return node

    # 3. 对剩余的 AUR 候选包进行一次批量信息查询
    aur_info_map = query_aur_info_batch(list(aur_candidates))
    
    aur_dependencies: List[Dict] = []
    # 4. 遍历原始排序的依赖列表以保持顺序和处理 provides
    for dep in sorted(list(all_deps)):
        cleaned_dep = clean_dependency_name(dep)
        if not cleaned_dep or cleaned_dep not in aur_candidates:
            continue
        
        actual_aur_pkg_name = None
        # 4a. 检查批量获取的结果中是否有直接匹配
        if cleaned_dep in aur_info_map:
            actual_aur_pkg_name = cleaned_dep
        else:
            # 4b. 如果直接匹配失败，再单独查询 provides (这是无法批量化的)
            provider_pkg = find_aur_provider(cleaned_dep)
            if provider_pkg and not find_official_alternative(provider_pkg):
                 actual_aur_pkg_name = provider_pkg
        
        if actual_aur_pkg_name:
            if actual_aur_pkg_name == cleaned_dep:
                print(f"[+] 发现纯 AUR 依赖: '{cleaned_dep}'")
            else:
                print(f"[+] 发现纯 AUR 依赖: '{cleaned_dep}' (由 AUR 包 '{actual_aur_pkg_name}' 提供)")
            
            subtree = build_aur_dependency_tree(actual_aur_pkg_name)
            if subtree:
                aur_dependencies.append(subtree)
        else:
             print(f"[-] 警告: 依赖 '{cleaned_dep}' 在官方源和AUR中都找不到。跳过。")

    if aur_dependencies:
        node["dependencies"] = aur_dependencies
    
    return node


def main():
    print(f"[?] 检查根包 '{args.package_name}' 是否有官方源替代品...")
    official_alternative = find_official_alternative(args.package_name)

    if official_alternative:
        print(
            f"\n[✓] 分析完成：根软件包 '{args.package_name}' 可由官方软件包 '{official_alternative}' 满足。"
        )
        print("[i] 无需构建 AUR 依赖树，不修改任何文件。")
        sys.exit(0)

    print(f"[i] '{args.package_name}' 没有直接的官方替代品，开始构建纯 AUR 依赖树...")

    dependency_tree = build_aur_dependency_tree(args.package_name)

    if not dependency_tree:
        print(f"\n[-] 未能为 '{args.package_name}' 构建依赖树。", file=sys.stderr)
        sys.exit(1)

    if args.file:
        yaml_file = Path(args.file)
        data_to_write = {"packages": []}
        if yaml_file.is_file():
            with open(yaml_file, "r", encoding="utf-8") as f:
                try:
                    loaded_data = yaml.safe_load(f)
                    if isinstance(loaded_data, dict) and "packages" in loaded_data:
                        data_to_write = loaded_data
                except (yaml.YAMLError, ValueError):
                    pass

        existing_packages = [pkg["name"] for pkg in data_to_write.get("packages", [])]
        if args.package_name in existing_packages:
            print(
                f"\n[!] 警告: 包 '{args.package_name}' 已存在于 '{yaml_file}' 中。无需操作。"
            )
            sys.exit(0)

        data_to_write.setdefault("packages", []).append(dependency_tree)
        
        data_to_write["packages"].sort(key=lambda pkg: pkg["name"])

        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(
                data_to_write,
                f,
                Dumper=NoAliasDumper,
                indent=2,
                sort_keys=False,
                allow_unicode=True,
            )
        print(
            f"\n[✓] 成功将 '{args.package_name}' 的纯 AUR 依赖树更新到 '{yaml_file}'！"
        )
    else:
        print("\n" + "=" * 30)
        print("  纯 AUR 依赖树结果")
        print("=" * 30)
        print(
            yaml.dump(
                dependency_tree,
                Dumper=NoAliasDumper,
                indent=2,
                sort_keys=False,
                allow_unicode=True,
            )
        )


if __name__ == "__main__":
    main()