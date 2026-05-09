#!/usr/bin/env bash
set -euo pipefail

allowed_path="${1:?allowed artifact path required}"
payload="$(</dev/stdin)"

HOOK_INPUT="$payload" python3 - "$allowed_path" <<'PY'
import json
import os
import sys

allowed = sys.argv[1]
workspace = os.getcwd()

def normalize(path):
    if not path:
        return None
    if not os.path.isabs(path):
        path = os.path.join(workspace, path)
    return os.path.normpath(path)

allowed_abs = normalize(allowed)

try:
    data = json.loads(os.environ.get("HOOK_INPUT", "{}"))
except json.JSONDecodeError:
    print("Blocked: could not parse hook payload.", file=sys.stderr)
    sys.exit(2)

tool_input = data.get("tool_input") or data.get("toolInput") or {}
paths = []

for key in ("file_path", "filePath", "path", "notebook_path", "notebookPath"):
    value = tool_input.get(key)
    if isinstance(value, str):
        paths.append(value)

for key in ("edits", "patches"):
    values = tool_input.get(key)
    if isinstance(values, list):
        for item in values:
            if isinstance(item, dict):
                for path_key in ("file_path", "filePath", "path"):
                    value = item.get(path_key)
                    if isinstance(value, str):
                        paths.append(value)

if not paths:
    print(f"Blocked: write/edit tool did not expose a file path. Only {allowed} may be modified.", file=sys.stderr)
    sys.exit(2)

for path in paths:
    if normalize(path) != allowed_abs:
        print(f"Blocked: this agent may only modify {allowed}; attempted {path}.", file=sys.stderr)
        sys.exit(2)

sys.exit(0)
PY
