import os
from pathlib import Path

HTML_TEMPLATE_HEAD = """<!DOCTYPE html>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Packages</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #9DB2BF;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .container {
            display: flex;
            flex-direction: column;
            text-align: center;
            width: 60%;
            height: 80%;
            background-color: #DDE6ED;
            box-shadow: 0 4px 8px #526D82;
            border-radius: 8px;
            padding: 20px 0;
        }

        h2 {
            margin: 0;
            padding: 10px 0;
        }

        .list-container {
            flex: 1;
            overflow-y: auto;
            padding: 0 20px;
        }

        ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        li {
            padding: 15px 20px;
            border-bottom: 1px solid #eee;
            transition: background-color 0.3s, padding-left 0.3s;
        }

        li:last-child {
            border-bottom: none;
        }

        li:hover {
            background-color: #f9f9f9;
            padding-left: 30px;
        }

        li a {
            text-decoration: none;
            color: #333;
            display: block;
        }

        li a:hover {
            color: #1abc9c;
        }
    </style>
</head>

<body>
    <div class="container">
        <h2>Packages</h2>
        <div class="list-container">
            <ul>
"""

HTML_TEMPLATE_TAIL = """
            </ul>
        </div>
    </div>
</body>

</html>
"""

LI_TEMPLATE = """                <li>
                    <div style="display: flex; justify-content: space-between; width: 100%;">
                        <a style="text-align: left;" href="{file}">{file}</a>{size}
                    </div>
                </li>
"""


def pretty_size(size):
    if size < 1024:
        return f"{size} Bytes"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KiB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MiB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GiB"


def generate_html(directory):
    files = files = [
        (entry.name, entry.stat().st_size)
        for entry in os.scandir(directory)
        if entry.is_file()
    ]
    files.sort()

    html_content = [HTML_TEMPLATE_HEAD]
    exclude_files = [
        "index.html",
        "our.db",
        "our.db.sig",
        "our.files",
        "our.files.sig",
        "our.db.tar.gz",
        "our.db.tar.gz.sig",
        "our.files.tar.gz",
        "our.files.tar.gz.sig",
    ]

    for file, size in files:
        if file in exclude_files:
            continue
        html_content.append(LI_TEMPLATE.format(file=file, size=pretty_size(size)))

    html_content.append(HTML_TEMPLATE_TAIL)

    output_path = os.path.join(directory, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(html_content))

    print(f"index.html generated at {output_path}")


if __name__ == "__main__":
    directory = "x86_64"
    if Path(directory).is_dir():
        generate_html(directory)
    else:
        print(f"Directory '{directory}' not found.")
        exit(1)
