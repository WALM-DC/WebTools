import requests
import certifi
import csv
import json
from io import StringIO
from typing import List, Dict, Any, Optional, Tuple

ASSET_PREFIX = "D:\\inetpub\\wwwroot\\icom\\ICOM\\gfx\\"
# Hinweis: In den JSON-Strings steht meist "D:\\inetpub\\...\\gfx\\", nach json.loads ist das i.d.R. "D:\inetpub\...\gfx\"
# Das doppelte Backslash am Ende in ASSET_PREFIX ist Absicht, damit wir robust strippen.

STOFFE_CSV_URL = "https://walm-dc.github.io/WebTools/public/Stoffe.csv"
ASSETS_JSON_URL = "https://ig-creator.xxxlgroup.com/icom/assets.json"


def fetch_text(url: str) -> str:
    """Fetch URL content as text. Uses requests if available, else urllib."""
    try:
        r = requests.get(url, timeout=60, verify=False)
        r.raise_for_status()
        return r.content.decode("utf-8-sig", errors="replace")
    except ImportError:
        from urllib.request import urlopen, Request
        req = Request(url, headers={"User-Agent": "python"})
        with urlopen(req, timeout=60) as resp:
            return resp.read().decode("utf-8", errors="replace")


def fetch_json(url: str) -> Any:
    return json.loads(fetch_text(url))


def parse_stoffe_csv(csv_text: str) -> List[Dict[str, str]]:
    """
    Mirrors the JS indices:
      parts[2]=lieferantNr, [3]=lieferantName, [5]=modell, [6]=stoff, [7]=farbe, [8]=zusammensetzung
    Uses csv.reader (safer than split(',')).
    """
    stoff_list: List[Dict[str, str]] = []

    reader = csv.reader(StringIO(csv_text))
    for row in reader:
        if not row or all((c.strip() == "" for c in row)):
            continue
        # Guard for short lines
        if len(row) <= 8:
            continue

        stoff_list.append({
            "lieferantNr": row[2].strip(),
            "lieferantName": row[3].strip(),
            "modell": row[5].strip(),
            "stoff": row[6].strip().replace(" ", "_"),
            "farbe": row[7].strip(),
            "zusammensetzung": row[8].strip(),
        })
    # print(stoff_list)
    return stoff_list


def parse_assets(assets_data: Any) -> List[Dict[str, str]]:
    """
    assets_data is expected to be a list of strings (like in your JS: $.each(data, function(id, val){...}))
    Each string looks like: D:\inetpub\wwwroot\icom\ICOM\gfx\<lieferant>\<modell>\<textur>\<fileName>
    """
    full_asset_list: List[Dict[str, str]] = []
    seen_textur = set()

    if not isinstance(assets_data, list):
        raise ValueError("assets.json must be a JSON array (list).")

    for val in assets_data:
        if not isinstance(val, str) or val.strip() == "":
            continue

        # replicate: val.replace(prefix, '').split('\\')
        stripped = val.replace(ASSET_PREFIX, "")
        parts = stripped.split("\\")

        # Expect at least 4 segments: supplier, model, texture, filename
        if len(parts) < 4:
            continue

        supplier_raw = parts[0]
        entry = {
            "lieferant": supplier_raw.replace("XXXL", ""),
            "inOrExtern": "intern" if ("XXXL" not in supplier_raw) else "extern",
            "modell": parts[1],
            "textur": parts[2].replace(".geo", "").replace(".tex", ""),
            "fileName": parts[3],
        }

        textur_key = (entry["textur"] or "").lower()
        if textur_key in seen_textur:
            continue
        seen_textur.add(textur_key)
        full_asset_list.append(entry)

    # JS had fullAssetList.sort(sortList); sortList isn't shown, so we use a sensible deterministic sort:
    full_asset_list.sort(key=lambda x: (
        x.get("inOrExtern", ""),
        (x.get("lieferant") or "").lower(),
        (x.get("modell") or "").lower(),
        (x.get("textur") or "").lower(),
        (x.get("fileName") or "").lower(),
    ))

    return full_asset_list


def build_stoff_index(stoff_list: List[Dict[str, str]]) -> Dict[Tuple[str, str], List[Dict[str, str]]]:
    """
    Index by (modell_lower, stoff_lower) -> list of stoff entries.
    Supplier matching is done at lookup time (because it can match by Nr OR Name).
    """
    idx: Dict[Tuple[str, str], List[Dict[str, str]]] = {}
    for s in stoff_list:
        key = ((s.get("modell") or "").lower(), (s.get("stoff") or "").lower())
        idx.setdefault(key, []).append(s)
    return idx


def find_match_for_asset(
    asset: Dict[str, str],
    stoff_idx: Dict[Tuple[str, str], List[Dict[str, str]]]
) -> Optional[Dict[str, str]]:
    key = ((asset.get("modell") or "").lower(), (asset.get("textur") or "").lower())
    candidates = stoff_idx.get(key, [])
    if not candidates:
        return None

    a_lieferant = (asset.get("lieferant") or "").strip()
    a_lieferant_lower = a_lieferant.lower()

    for s in candidates:
        if (s.get("lieferantNr") or "").strip() == a_lieferant:
            return s
        if (s.get("lieferantName") or "").strip().lower() == a_lieferant_lower:
            return s

    return None


def combine(stoff_list: List[Dict[str, str]], assets_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
    stoff_idx = build_stoff_index(stoff_list)

    print(stoff_idx)

    combined: List[Dict[str, str]] = []
    for a in assets_list:
        match = find_match_for_asset(a, stoff_idx)
        farbe = match.get("farbe", "") if match else ""
        zusammensetzung = match.get("zusammensetzung", "") if match else ""

        combined.append({
            "lieferant": a.get("lieferant", ""),
            "inOrExtern": a.get("inOrExtern", ""),
            "modell": a.get("modell", ""),
            "textur": a.get("textur", ""),
            "fileName": a.get("fileName", ""),
            "farbe": farbe,
            "zusammensetzung": zusammensetzung,
        })

    return combined


def main(output_path: str = "stoffZusammensetzung.json") -> None:
    stoffe_csv_text = fetch_text(STOFFE_CSV_URL)
    assets_data = fetch_json(ASSETS_JSON_URL)

    stoff_list = parse_stoffe_csv(stoffe_csv_text)
    assets_list = parse_assets(assets_data)
    combined = combine(stoff_list, assets_list)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(combined)} records to {output_path}")


if __name__ == "__main__":
    main()
