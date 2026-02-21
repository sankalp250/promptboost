"""
Gather optional project context (README, package.json, etc.) from workspace
for Option A client-sent context. Keeps code on client; server uses it for enhancement.
"""
from pathlib import Path

# Max chars per file and total to avoid huge payloads
MAX_README_CHARS = 2000
MAX_MANIFEST_CHARS = 1500
MAX_TOTAL_CONTEXT_CHARS = 5000

MANIFEST_FILES = [
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
]
README_NAMES = ["README.md", "readme.md", "README.txt"]


def gather_project_context(workspace_path: str | None) -> str | None:
    """
    Read README and manifest files from workspace and return a single context string.
    Returns None if workspace_path is missing/invalid or no files found.
    """
    if not workspace_path or not workspace_path.strip():
        return None
    root = Path(workspace_path.strip()).resolve()
    if not root.is_dir():
        return None
    parts: list[str] = []
    total = 0

    for name in README_NAMES:
        p = root / name
        if p.is_file():
            try:
                text = p.read_text(encoding="utf-8", errors="replace").strip()
                snippet = text[:MAX_README_CHARS]
                if len(text) > MAX_README_CHARS:
                    snippet += "\n..."
                parts.append(f"[{name}]\n{snippet}")
                total += len(snippet)
                break
            except OSError:
                pass
        if total >= MAX_TOTAL_CONTEXT_CHARS:
            break

    for name in MANIFEST_FILES:
        if total >= MAX_TOTAL_CONTEXT_CHARS:
            break
        p = root / name
        if p.is_file():
            try:
                text = p.read_text(encoding="utf-8", errors="replace").strip()
                snippet = text[:MAX_MANIFEST_CHARS]
                if len(text) > MAX_MANIFEST_CHARS:
                    snippet += "\n..."
                parts.append(f"[{name}]\n{snippet}")
                total += len(snippet)
            except OSError:
                pass

    if not parts:
        return None
    return "\n\n".join(parts)[:MAX_TOTAL_CONTEXT_CHARS]
