#!/usr/bin/env python3

import argparse
import sys
import yaml


def main():
    parser = argparse.ArgumentParser(
        description="Extract dependencies for a specific package from packages.yaml."
    )
    parser.add_argument("yaml_file", help="Path to the packages.yaml file.")
    parser.add_argument("package_name", help="Name of the package to query.")
    args = parser.parse_args()

    try:
        with open(args.yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: File not found '{args.yaml_file}'", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse YAML: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, dict) or "packages" not in data:
        sys.exit(0)

    for pkg in data["packages"]:
        if pkg.get("name") == args.package_name:
            dependencies = pkg.get("dependencies", [])
            if dependencies:
                # Print dependencies separated by space
                print(" ".join(dependencies))
            return

    # Package not found or no dependencies, output nothing
    sys.exit(0)


if __name__ == "__main__":
    main()
