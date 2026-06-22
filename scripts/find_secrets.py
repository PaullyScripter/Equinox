import re
import os

PATTERNS = [
    r'["\']?(?:token|key|secret|password|api|auth|bearer|client_id|client_secret)["\']?\s*[:=]\s*["\'](.+?)["\']',
    r'["\'](sk-[A-Za-z0-9]{20,})["\']',                  # OpenAI style
    r'["\']([A-Za-z0-9_\-]{24}\.[A-Za-z0-9_\-]{6}\.[A-Za-z0-9_\-]{27})["\']',  # Discord bot token
    r'["\']([A-Za-z0-9]{32,})["\']',                     # generic long string
]

def search_file(path):
    secrets = []
    with open(path, "r", errors="ignore") as f:
        for line in f:
            for pattern in PATTERNS:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    secrets.append(match.group(1))
    return secrets

root = "."
found = {}

for folder, _, files in os.walk(root):
    for file in files:
        if file.endswith(".py"):
            p = os.path.join(folder, file)
            secrets = search_file(p)
            if secrets:
                found[p] = secrets

print("\n=== POSSIBLE SECRETS FOUND ===")
for file, secrets in found.items():
    print(f"\n{file}:")
    for sec in secrets:
        print(f"  {sec}")
