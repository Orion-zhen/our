import argparse
import json
import sys
import yaml


def find_packages(nodes: list, lto_filter: bool, recursive: bool = False):
    """
    一个递归生成器，用于深度优先遍历依赖森林。

    Args:
        nodes (list): 当前层的软件包节点列表。
        lto_filter (bool): 要筛选的 lto 标志 (True 或 False)。

    Yields:
        str: 匹配筛选条件的软件包名称。
    """
    # 遍历当前层的所有节点 (包)
    for node in nodes:
        # 检查当前节点的 'lto' 字段是否与筛选条件匹配
        # 使用 .get() 可以安全地处理节点没有 'lto' 字段的情况
        # 无 lto 时默认为启用 lto
        deps = node.get("dependencies", [])
        if not isinstance(deps, list):
            deps = [deps]
        deps_str = " ".join(deps)

        excludes = node.get("exclude", [])
        if not isinstance(excludes, list):
            excludes = [excludes]
        excludes_str = " ".join(excludes)

        base = node.get("base", "")

        env_vars = node.get("env", [])
        if not isinstance(env_vars, list):
            env_vars = [env_vars] if env_vars else []
        env_str = "\n".join(str(e) for e in env_vars)

        item = {
            "name": node["name"],
            "dependencies": deps_str,
            "exclude": excludes_str,
            "base": base,
            "env": env_str
        }

        if lto_filter and node.get("lto") is not False:
                yield item
        elif not lto_filter and node.get("lto") is False:
                yield item

        # 如果存在 'dependencies' 键，则递归进入下一层
        if recursive and "dependencies" in node and node["dependencies"]:
            # 'yield from' 是一个优雅的语法，用于链接生成器
            yield from find_packages(node["dependencies"], lto_filter, recursive)


def main():
    """
    主函数，处理命令行参数、文件读取和结果输出。
    """
    # 1. 设置命令行参数解析器
    parser = argparse.ArgumentParser(
        description="解析软件包依赖 YAML 文件，并根据 LTO 标志筛选包名。"
    )

    parser.add_argument("yaml_file", type=str, help="输入的 packages.yaml 文件路径")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="递归地遍历依赖树，并返回所有匹配的包. 在 GitHub Actions 中不应开启.",
    )

    # 创建一个互斥组，确保 --lto 和 --no-lto 不能同时使用
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--lto", action="store_true", help="输出所有 lto: true 的软件包")
    group.add_argument(
        "--no-lto", action="store_true", help="输出所有 lto: false 的软件包"
    )

    args = parser.parse_args()

    # 2. 根据参数确定筛选条件
    lto_filter_value = True if args.lto else False

    # 3. 读取并解析 YAML 文件
    try:
        with open(args.yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"错误: 文件未找到 '{args.yaml_file}'", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"错误: YAML 文件解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 校验文件顶层结构
    if "packages" not in data or not isinstance(data.get("packages"), list):
        print(
            "错误: YAML 文件必须包含一个名为 'packages' 的顶层列表。", file=sys.stderr
        )
        sys.exit(1)

    # 4. 执行遍历和筛选
    package_forest = data["packages"]
    # 将生成器结果转换为列表
    matching_packages = list(find_packages(package_forest, lto_filter_value))

    # 5. 以单行 JSON 列表格式输出结果
    print(json.dumps(matching_packages))


if __name__ == "__main__":
    main()
