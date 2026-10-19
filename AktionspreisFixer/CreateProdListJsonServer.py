import asyncio
import os, os.path
import json
import csv
from unittest import case
import requests
import xml.etree.ElementTree as ET
import urllib3
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import ssl
import shutil
from datetime import datetime

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

headerList = ["Artikelnummer", "live", "konfigurierbar", "Schiene", "Land"]
onlineList = {}
api_tasks = []
search_path = (r"D:\inetpub\wwwroot\icom\ICOM")
output_pathArchive = r"D:\inetpub\wwwroot\idm\XMLLister\kkbmArchive.json"
output_pathList = r"D:\inetpub\wwwroot\idm\XMLLister\list.json"

BASE_URL = "https://services.ist.lutz.gmbh/HybrisProductDelivery/clients/{}/assortmentLines/{}/productNumbers/{}/{}"
####
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def save_kkbmArchive_file(data):
    with open(output_pathArchive, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_json_file(data):
    with open(output_pathList, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Mandanten
def code_from_rail(country: str, rail: str) -> int:
    country = country.lower()
    rail = rail.lower()

    match rail:
        case "lu":
            if country == "de":
                return '0Z'
            return '0L'
        case "mm":
            if country == "hu":
                return '0Y'
            return '0M'
        case "mx":
            if country == "cz" or country == "sk":
                return '1X'
            return '0X'
        case _:
            return -1

# Zielmärkte
def code_from_country(country: str) -> int:
    country = country.lower()

    match country:
        case "at":
            return 0
        case "si":
            return 2
        case "hr":
            return 3
        case "rs":
            return 6
        case "pl":
            return 9
        case "cz":
            return 10
        case "sk":
            return 11
        case "hu":
            return 12
        case "se":
            return 13
        case "ro":
            return 14
        case "ch":
            return 15
        case "de":
            return 17
        case _:
            return -1      

def get_api_data(task):

    mandant = task['locale']
    rail = task['brand']
    product_number = task['productNumber']
    kkbm = task['KkBm']
    variant_id = task['variantId']
    modelId = task["modelId"]

    mandatNr = code_from_country(mandant)
    railCode = code_from_rail(mandant, rail)

    url = BASE_URL.format(mandatNr, railCode, product_number, variant_id)

    online_status = False
    cfg_exists = False

    try:
        response = requests.get(url, verify=False, timeout=20)

        try:
            data = response.json()

        except:
            print(f"[ERROR] Failed to parse JSON for {product_number} variant {variant_id}. Response content: {response.text}")

        # error = data.get("error")
        export_action = data.get("ExportAction", "ERROR")

        # if product_number == '0023100028':
        #     print(variant_id, export_action, url)

        if export_action == "ERROR":
            # online_status = False
            # cfg_exists = False
            kkbm = "NO"
        elif export_action != "OFFLINE":
            config = data.get("Configuration")
            config_id = config.get("ConfigurationId", "")
            system_id = config.get("ConfigurationSystemId", "")

            kkbm = data.get("Prices")['Price'][0]['KkBm']

            if config:
                online_status = True
                if config_id or system_id:
                    cfg_exists = True
                else:
                    cfg_exists = False
            # else:
            #     online_status = False
            #     cfg_exists = False

    except Exception as e:
        # online_status = False
        # cfg_exists = False
        print(f"[ERROR] API request failed for {product_number} variant {variant_id}: {e}")

    return {
        "modelId": modelId,
        "variantId": variant_id,
        "productNumber": product_number,
        "KkBm": kkbm,
        "online": online_status,
        "konfigurable": cfg_exists
    }
    
async def fetch_all(task_list):
    loop = asyncio.get_running_loop()
    results = []

    with ThreadPoolExecutor(max_workers=30) as pool:
        tasks = [
            loop.run_in_executor(
                pool,
                get_api_data,   # same function as before
                task                 # pass the entire task object
            )
            for task in task_list
        ]

        for completed in asyncio.as_completed(tasks):
            results.append(await completed)

    return results


def load_json_file(file_path, default_value):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default_value
    except json.JSONDecodeError:
        print(f"Warning: Could not read valid JSON from {file_path}")
        return default_value


def normalize_kkbm(kkbm_data):
    """
    Normalizes KkBm data for comparison.

    The order of variant IDs inside the lists is ignored, so a different
    processing order does not incorrectly create a new archive entry.
    """
    if not isinstance(kkbm_data, dict):
        return {}

    normalized = {}

    for key, value in kkbm_data.items():
        if isinstance(value, list):
            normalized[str(key)] = sorted(value, key=str)
        else:
            normalized[str(key)] = value

    return dict(sorted(normalized.items()))


def get_kkbm_history_entries(archive_record):
    """
    Returns all timestamped KkBm entries from one archive record.

    This also supports older entries using only YYYY-MM-DD as the key.
    """
    history_entries = {}

    if not isinstance(archive_record, dict):
        return history_entries

    metadata_keys = {
        "productNumber",
        "brand",
        "locale",
    }

    for key, value in archive_record.items():
        if (
            key not in metadata_keys
            and isinstance(value, dict)
            and "KkBm" in value
        ):
            history_entries[key] = value

    return history_entries

def update_kkbm_archive(full_model_list, output_path):
    """
    Compares the current KkBm data with the latest archived KkBm data.

    A new timestamped archive entry is created only when KkBm changed.
    Existing timestamped entries are preserved.
    """
    kkbm_archive_list = load_json_file(output_path, {})

    for model_id, model_data in full_model_list.items():
        current_kkbm = deepcopy(model_data.get("KkBm", {}))

        archive_record = kkbm_archive_list.get(model_id)

        if not isinstance(archive_record, dict):
            archive_record = {}

        # Keep the current model metadata up to date.
        archive_record["productNumber"] = model_data.get("productNumber")
        archive_record["brand"] = model_data.get("brand")
        archive_record["locale"] = model_data.get("locale")

        history_entries = get_kkbm_history_entries(archive_record)

        should_add_new_entry = False

        if not history_entries:
            # No previous archive exists for this model.
            should_add_new_entry = True
        else:
            # Timestamp format sorts correctly chronologically.
            latest_timestamp = max(history_entries.keys())
            latest_kkbm = history_entries[latest_timestamp].get("KkBm", {})

            if normalize_kkbm(latest_kkbm) != normalize_kkbm(current_kkbm):
                should_add_new_entry = True

        if should_add_new_entry:
            timestamp = datetime.now().strftime("%Y-%m-%d")

            archive_record[timestamp] = {
                "KkBm": current_kkbm
            }

            print(
                f"KkBm changed for model {model_id}. "
                f"Added archive entry {timestamp}."
            )
        else:
            print(
                f"No KkBm change for model {model_id}. "
                f"Archive remains unchanged."
            )

        kkbm_archive_list[model_id] = archive_record

    save_kkbmArchive_file(kkbm_archive_list)

def find_all_json(root_path):
    fullModelList = {}
    kkbmArchiveList = {}
    fullConditionsList = {}
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.endswith('.json') and filename.find(' ')==-1:
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # if contains_target_values(data, target_values):
                        if contains_target_keys(data, {'catalog'}):
                            model_object = {
                                data['catalog'].split('.')[0] +'.'+ filename.split('.')[0]: {
                                    'fileName': filename.split('.')[0],
                                    'productNumber': '',
                                    'productVariants': '',
                                    'variantConfig': '',
                                    'variantOnline': '',
                                    'KkBm': [],
                                    'online': False,
                                    'konfig':False,
                                    'modelName': filename.split('@')[0],
                                    'locale': filename.split('@')[1].split('.')[0],
                                    'currency': data.get('currency', ''),  
                                    'catalog': data.get('catalog', ''), 
                                    'model': data.get('model', ''),
                                    'brand': data.get('brand', ''),
                                    'brandName': data.get('brandName', ''),
                                    'productGroup': data.get('productGroup', ''),
                                    'description': data.get('description', ''),
                                    'preis': data.get('settings',{}).get('kaa1', ''),
                                    'entlastung': data.get('settings',{}).get('entlastung', ''),
                                    'aktion': data.get('settings',{}).get('aktion', ''),
                                    'pricing': data.get('settings', {}).get('pricing', ''),
                                    'properties': data.get('properties', []),
                                    'sets': data.get('sets', [])
                                }
                            }
                            fullModelList.update(model_object)

                        if filename.startswith('conditions'):
                            conditions_object = data['sets']
                            fullConditionsList.update(conditions_object)

                except Exception as e:
                    print(f"[ERROR] Unexpected error with {file_path}: {e}")
    
    for modelId, modelEntry in fullModelList.items():
        try:
            modesIdShort = fullModelList[modelId]['fileName']
            if fullConditionsList[modesIdShort] != '':
                for innerId, conditionEntry in fullConditionsList[modesIdShort].items():
                    fullModelList[modelId]['productNumber'] = conditionEntry.get('productNo')
                    if fullModelList[modelId]['description'] == '':
                        fullModelList[modelId]['description'] = conditionEntry.get('description')
                    api_tasks.append({
                        "modelId": modelId,
                        "locale": fullModelList[modelId]['locale'],
                        "brand": fullModelList[modelId]['brand'],
                        "productNumber": fullModelList[modelId]['productNumber'],
                        "KkBm": fullModelList[modelId]['KkBm'],
                        "variantId": innerId
                    })
        except KeyError as e:
            print(f'KeyError: {e} not found in conditions.json')

    results = asyncio.run(fetch_all(api_tasks))
    for r in results:
        modelId = r["modelId"]
        variantId = r["variantId"]

        # ensure KkBm container is a dict
        if not isinstance(fullModelList[modelId].get("KkBm"), dict):
            fullModelList[modelId]["KkBm"] = {}

        raw = r.get("KkBm")

        # normalize: "11" -> "11", []/None -> ""
        kkbm = raw if isinstance(raw, str) else ""

        fullModelList[modelId]["KkBm"].setdefault(kkbm, [])
        fullModelList[modelId]["KkBm"][kkbm].append(variantId)

        if r["online"] and r["konfigurable"] and (kkbm != "1L" and kkbm != ""):
            fullModelList[modelId]["variantConfig"] += variantId + " / "
            fullModelList[modelId]["online"] = True
            fullModelList[modelId]["konfig"] = True

        elif r["online"] and not r["konfigurable"]:
            fullModelList[modelId]["variantOnline"] += variantId + " / "
            fullModelList[modelId]["online"] = True

        else:
            fullModelList[modelId]["productVariants"] += variantId + " / "

        # kkbmArchiveList[modelId] = {
        #     "productNumber": fullModelList[modelId]["productNumber"],
        #     "brand": fullModelList[modelId]["brand"],
        #     "locale": fullModelList[modelId]["locale"],
        #     datetime.now().strftime("%Y-%m-%d"): {
        #         "KkBm": fullModelList[modelId]["KkBm"]
        #     }
        # }

    update_kkbm_archive(
        full_model_list=fullModelList,
        output_path=output_pathArchive
    )
        
    # save_kkbmArchive_file(kkbmArchiveList)
    save_json_file(fullModelList)

def contains_target_values(data, target_values):
    """
    Recursively check if any of the target values exist in the JSON data.
    
    :param data: JSON-parsed Python object.
    :param target_values: Set or list of values to look for.
    :return: True if any target value is found, False otherwise.
    """
    if isinstance(data, dict):
        return any(contains_target_values(v, target_values) for v in data.values())
    elif isinstance(data, list):
        return any(contains_target_values(item, target_values) for item in data)
    else:
        return data in target_values
    
def contains_target_keys(data, target_keys):
    """
    Recursively check if any of the target keys exist in the JSON data.

    :param data: JSON-parsed Python object.
    :param target_keys: Set of keys to look for.
    :return: True if any target key is found, False otherwise.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key in target_keys:
                return True
            if contains_target_keys(value, target_keys):
                return True
    elif isinstance(data, list):
        return any(contains_target_keys(item, target_keys) for item in data)
    return False

if __name__ == "__main__":
    find_all_json(search_path)