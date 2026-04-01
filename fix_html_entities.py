
import os
import re

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = content.replace('&gt;', '>')
    content = content.replace('&lt;', '<')
    content = content.replace('&amp;', '&')
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {file_path}")
    else:
        print(f"No changes needed: {file_path}")

if __name__ == "__main__":
    backend_dir = "backend"
    for filename in os.listdir(backend_dir):
        if filename.endswith(".py"):
            fix_file(os.path.join(backend_dir, filename))
