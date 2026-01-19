import asyncio
import os, os.path
import json
import csv
from unittest import case
import requests
import xml.etree.ElementTree as ET
import urllib3
from concurrent.futures import ThreadPoolExecutor
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

headerList = ["Artikelnummer", "live", "konfigurierbar", "Schiene", "Land"]
onlineList = {}
api_tasks = []
BASE_URL = "https://services.ist.lutz.gmbh/HybrisProductDelivery/clients/{}/assortmentLines/{}/productNumbers/{}/{}"

def save_json_file(data):
    output_path = "F:\WebTools\public\list.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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
    variant_id = task['variantId']
    modelId = task["modelId"]

    mandatNr = code_from_country(mandant)
    railCode = code_from_rail(mandant, rail)

    url = BASE_URL.format(mandatNr, railCode, product_number, variant_id)

    try:
        response = requests.get(url, verify=False, timeout=10)
      
        try:
            data = response.json()
        except:
            online_status = False
            cfg_exists = False

        error = data.get("error")

        if error:
            online_status = False
            cfg_exists = False
        else:
            config = data.get("Configuration")
            config_id = config.get("ConfigurationId", "")
            system_id = config.get("ConfigurationSystemId", "")

            if config:
                online_status = True
                if config_id or system_id:
                    cfg_exists = True
                else:
                    cfg_exists = False
            else:
                online_status = False
                cfg_exists = False

    except Exception as e:
        online_status = False
        cfg_exists = False

    return {
        "modelId": modelId,
        "variantId": variant_id,
        "productNumber": product_number,
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

def find_all_json(root_path):
    fullModelList = {}
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
                                    'properties': data.get('properties', [])
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
                        "variantId": innerId
                    })
        except KeyError as e:
            print(f'KeyError: {e} not found in conditions.json')

    results = asyncio.run(fetch_all(api_tasks))
    for r in results:
        modelId = r["modelId"]
        variantId = r["variantId"]

        if r["online"] and r["konfigurable"]:
            fullModelList[modelId]["variantConfig"] += variantId + " / "
            fullModelList[modelId]["online"] = True
            fullModelList[modelId]["konfig"] = True

        elif r["online"] and not r["konfigurable"]:
            fullModelList[modelId]["variantOnline"] += variantId + " / "
            fullModelList[modelId]["online"] = True

        else:
            fullModelList[modelId]["productVariants"] += variantId + " / "

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
    search_path = (r"C:\xxxlutz\IG-Creator\XXXLutz\ICOM")
    find_all_json(search_path)