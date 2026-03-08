from __future__ import annotations

import re
from pathlib import Path
from typing import Set


def sanitize_filename(name: str, default: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    cleaned = cleaned.strip("._-")
    return cleaned or default


def unique_path(path: Path, used: Set[str]) -> Path:
    candidate = path
    stem = path.stem
    suffix = path.suffix
    index = 1

    while str(candidate).lower() in used or candidate.exists():
        candidate = path.with_name(f"{stem}_{index}{suffix}")
        index += 1

    used.add(str(candidate).lower())
    return candidate
