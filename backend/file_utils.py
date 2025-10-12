import os

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def search_files(query, base_dir):
    results = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith((".py", ".js", ".html", ".css", ".txt")):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        if query.lower() in f.read().lower():
                            results.append(os.path.relpath(path, base_dir))
                except:
                    continue
    return results