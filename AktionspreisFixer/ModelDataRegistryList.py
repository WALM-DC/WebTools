import requests
import json

combined_registry = []

BASE_URL = "https://ig-creator.xxxlgroup.com/idm/"

def extract_markets(markets):
    market_array = []

    if not isinstance(markets, list):
        return market_array  # unexpected structure → skip

    for market_block in markets:

        print("DEBUG market_block =", repr(market_block))
        # Case A — expected dict
        if isinstance(market_block, dict):
            for k, v in market_block.items():
                market_array.append(f"{k}: {v}")

        # Case B — list (rare but possible)
        elif isinstance(market_block, list):
            for item in market_block:
                if isinstance(item, dict):
                    for k, v in item.items():
                        market_array.append(f"{k}: {v}")

        # Case C — string (JS loops characters, but that makes no sense)
        elif isinstance(market_block, str):
            # Your JS code would treat each character as a key…  
            # This is useless, so we SKIP it instead.
            continue

        # Case D — anything else → skip
        else:
            continue

    return market_array

def combine_registries(cur_registry, file_name):
    for key, value in cur_registry.get("Domains", {}).items():

        # Skip entries without ComService
        com_service = value.get("ComService")
        if com_service is None:
            continue

        address_array = []

        # -------- CASE 1: No setups (single address) --------
        if com_service.get("Setups") is None:

            # Collect markets
            market_array = []
            markets = com_service.get("Markets", [])
            market_array = extract_markets(markets)

            print("ID:", key, "Markets raw:", com_service.get("Markets"))

            # Build final address string
            address_clean = com_service["Address"].replace(BASE_URL, "")
            address_array.append(
                f"{address_clean}\nMarkets: {', '.join(market_array)}"
            )

        # -------- CASE 2: Setups present (multiple possible formats) --------
        else:
            setups = com_service["Setups"]

            # Setup as dictionary
            if isinstance(setups, dict):
                setup_iter = setups.values()
            # Setup as list
            elif isinstance(setups, list):
                setup_iter = setups
            else:
                print("WARNING: Unknown setups type:", type(setups))
                continue

            # Loop through each setup
            for setup_value in setup_iter:
                market_array = []

                # Markets live inside each setup
                markets = setup_value.get("Markets", [])
                market_array = extract_markets(markets)

                print("ID:", key, "Setup Markets raw:", setup_value.get("Markets"))

                # Build
                address_clean = setup_value["Address"].replace(BASE_URL, "")
                address_array.append(
                    f"{address_clean}\nMarkets: {', '.join(market_array)}"
                )

        # -------- Build entry object --------
        entry = {
            "ID": key,
            "FileName": file_name,
            "Scope": value.get("Scope"),
            "Address": address_array,
        }

        # -------- Avoid duplicates by ID (case-insensitive) --------
        exists = any(item["ID"].lower() == key.lower() for item in combined_registry)
        if not exists:
            combined_registry.append(entry)


def read_and_show_json():
    urls = [
        ("https://ig-creator.xxxlgroup.com/icom/ICOM/_registry-moebelix.json", "moebelix"),
        ("https://ig-creator.xxxlgroup.com/icom/ICOM/_registry-moemax.json", "moemax"),
        ("https://ig-creator.xxxlgroup.com/icom/ICOM/_registry-xxxl.json", "xxxl"),
        ("https://ig-creator.xxxlgroup.com/icom/ICOM/_registry.json", "registry"),
    ]

    for url, name in urls:
        response = requests.get(url)
        if response.ok:
            text = response.content.decode("utf-8-sig")
            data = json.loads(text)
            combine_registries(data, name)


read_and_show_json()
print(combined_registry)