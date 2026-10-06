import os
import requests
import csv
import json
import operator
from io import StringIO
from typing import Dict, List, Tuple, Optional, Any
import urllib3
import requests
from pathlib import Path

ROOT = Path(r"D:\inetpub\wwwroot\icom\ICOM\gfx")
OUTPUT_FILE = Path(__file__).resolve().parent / "stoffeIG.json"

def get_assets(root: Path) -> list[dict[str, str]]:
    candidates = []

    # Sort paths first so duplicate handling is deterministic
    files = sorted(
        (
            file_path
            for file_path in root.rglob("*")
            if file_path.is_file()
            and file_path.suffix.lower() in {".png", ".jpeg", ".jpg"}
        ),
        key=lambda path: str(path).casefold(),
    )

    for file_path in files:
        relative_parts = file_path.relative_to(root).parts

        # Expected structure:
        # lieferant / ordner / textur / fileName
        if len(relative_parts) < 4:
            print(f"Skipping unexpected path: {file_path}")
            continue

        asset = {
            "lieferant": relative_parts[0],
            "ordner": relative_parts[1],
            "textur": relative_parts[-2],
            "fileName": relative_parts[-1],
        }

        candidates.append(asset)

    # Keep only one entry per lieferant + textur combination
    unique_assets = {}

    for asset in candidates:
        unique_key = (
            asset["lieferant"].casefold(),
            asset["textur"].casefold(),
        )

        unique_assets.setdefault(unique_key, asset)

    return sorted(
        unique_assets.values(),
        key=lambda asset: (
            asset["lieferant"].casefold(),
            asset["ordner"].casefold(),
            asset["textur"].casefold(),
            asset["fileName"].casefold(),
        ),
    )

def write_assets_json(assets: list[dict[str, str]], output_file: Path) -> None:
    output_file.write_text(
        json.dumps(
            assets,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

if __name__ == "__main__":
    assets = get_assets(ROOT)
    write_assets_json(assets, OUTPUT_FILE)

    print(f"Created: {OUTPUT_FILE}")
    print(f"Count: {len(assets)}")
