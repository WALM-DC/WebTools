import os
import requests
import csv
import json
import operator
from io import StringIO
from typing import Dict, List, Tuple, Optional, Any
import urllib3

ASSET_PREFIX = "D:\\inetpub\\wwwroot\\icom\\ICOM\\gfx\\"
# Hinweis: In den JSON-Strings steht meist "D:\\inetpub\\...\\gfx\\", nach json.loads ist das i.d.R. "D:\inetpub\...\gfx\"
# Das doppelte Backslash am Ende in ASSET_PREFIX ist Absicht, damit wir robust strippen.

STOFFE_CSV_URL = "F:\\WebTools\\public\\Stoffe.csv"
ASSETS_JSON_URL = "https://ig-creator.xxxlgroup.com/idm/XMLLister/assets.json"
MODEL_JSON_URL = "https://walm-dc.github.io/WebTools/public/list.json"

EXPECTED_HEADERS = {"Schiene", "Lieferant", "Modell", "Stoffname", "Farbe", "Zusammensetzung"}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def norm(s: Any) -> str:
    return str(s or "").strip()

def low(s: Any) -> str:
    return norm(s).lower()

def build_stoff_index(stoff_list: List[Dict[str, str]]):
    """
    Index by (modell_lower, stoff_lower) -> list of stoff rows
    (supplier matching is done afterwards)
    """
    idx: Dict[Tuple[str, str], List[Dict[str, str]]] = {}
    for s in stoff_list:
        key = (low(s.get("modell")), low(s.get("stoff")))
        if key == ("", ""):
            continue
        idx.setdefault(key, []).append(s)
    return idx

def read_text(source: str) -> str:
    # Local file?
    if os.path.exists(source):
        with open(source, "rb") as f:
            return f.read().decode("utf-8-sig", errors="replace")

    # Otherwise treat as URL
    r = requests.get(source, timeout=60, verify=False)
    r.raise_for_status()
    return r.content.decode("utf-8-sig", errors="replace")

def read_json(source: str):
    return json.loads(read_text(source).lstrip("\ufeff"))

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
    text = fetch_text(url)
    return json.loads(text.lstrip("\ufeff"))

def parse_stoffe_csv(csv_text: str) -> List[Dict[str, str]]:
    csv_text = csv_text.lstrip("\ufeff")
    lines = csv_text.splitlines()

    # Find the real header line index
    header_idx: Optional[int] = None
    for i, line in enumerate(lines[:200]):  # scan first N lines
        # cheap check before csv parsing
        if any(h in line for h in ("Schiene", "Modell", "Stoffname")):
            header_idx = i
            break

    if header_idx is None:
        raise ValueError("Could not find header row (Schiene/Modell/Stoffname) in Stoffe.csv")

    sliced = "\n".join(lines[header_idx:])

    reader = csv.DictReader(StringIO(sliced), delimiter=",")

    # Normalize fieldnames (strip spaces)
    if reader.fieldnames:
        reader.fieldnames = [fn.strip() if fn is not None else "" for fn in reader.fieldnames]

    stoff_list: List[Dict[str, str]] = []
    for row in reader:
        if not row:
            continue
        if all((str(v or "").strip() == "" for v in row.values())):
            continue

        stoff_list.append({
            "schiene": (row.get("Schiene") or "").strip(),
            "lieferantNr": (row.get("Lieferantennr.") or "").strip(),
            "lieferantName": (row.get("Lieferant") or "").strip(),
            "modell": (row.get("Modell") or "").strip(),
            "stoff": (row.get("Stoffname") or "").strip(),
            "farbe": (row.get("Farbe") or "").strip(),
            "zusammensetzung": (row.get("Zusammensetzung") or "").strip(),
        })

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

        stripped = val.replace(ASSET_PREFIX, "")
        parts = stripped.split("\\")

        # Expect at least 4 segments: supplier, model, texture, filename
        if len(parts) < 4:
            continue

        supplier_raw = parts[0]
        entry = {
            "lieferant": supplier_raw.replace("XXXL", ""),
            "inOrExtern": "Intern" if ("XXXL" not in supplier_raw) else "Extern",
            "ordner": parts[1],
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
        (x.get("ordner") or "").lower(),
        (x.get("textur") or "").lower(),
        (x.get("fileName") or "").lower(),
    ))

    return full_asset_list

def find_match(asset: Dict[str, str],
               stoff_idx: Dict[Tuple[str, str], List[Dict[str, str]]],
               allow_fallback_unique_stoff: bool = False) -> Optional[Dict[str, str]]:

    # a_modell = low(asset.get("modell"))
    a_textur = low(asset.get("textur"))
    a_liefer = norm(asset.get("lieferant"))
    a_liefer_l = a_liefer.lower()

    # 1) Strong match: modell + stoff/textur + supplier
    candidates = stoff_idx.get((a_textur), [])
    for s in candidates:
        if norm(s.get("lieferantNr")) == a_liefer:
            return s
        if low(s.get("lieferantName")) == a_liefer_l:
            return s

    # 2) Optional fallback: if modell missing, match by stoff/textur only if unique
    if allow_fallback_unique_stoff and a_textur:
        # build this once outside if you need it; shown inline for clarity
        pass

    return None

def combine(stoff_list: List[Dict[str, str]], assets_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
    combined: List[Dict[str, str]] = []
    match: Optional[Dict[str, str]] = None
    for a in assets_list:
        for s in stoff_list:
            if s.get("stoff").lower() == a.get("textur").lower():
                match = s
                break

            schiene = match.get("schiene", "") if match else ""
            lieferNr = match.get("lieferantNr", "") if match else ""
            lieferName = match.get("lieferantName", "") if match else ""
            modell = match.get("modell", "") if match else ""
            farbe = match.get("farbe", "") if match else ""
            zusammensetzung = match.get("zusammensetzung", "") if match else ""
                
        combined.append({
            "schiene": schiene,
            "lieferantNr": lieferNr,
            "lieferantName": lieferName,
            "inOrExtern": a.get("inOrExtern", ""),
            "ordner": a.get("ordner", ""),
            "modell": modell,
            "textur": a.get("textur", ""),
            "fileName": a.get("fileName", ""),
            "farbe": farbe,
            "zusammensetzung": zusammensetzung,
        })

    return combined

def main(output_path: str = "F:\\WebTools\\public\\stoffZusammensetzung.json") -> None:
    stoffe_csv_text = read_text(STOFFE_CSV_URL)
    assets_data = fetch_json(ASSETS_JSON_URL)

    stoff_list = parse_stoffe_csv(stoffe_csv_text)
    assets_list = parse_assets(assets_data)

    combined = combine(stoff_list, assets_list)

    # Sort combined list by lieferantNr, then by modell, then by textur
    combined.sort(key=operator.itemgetter("lieferantNr", "modell", "textur"))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(combined)} records to {output_path}")

if __name__ == "__main__":
    main()
