import os, os.path
import json
import csv

# Take unified list from 4 registries
# extract model jsons based on registry entries


headerList = ["Artikelnummer", "live", "konfigurierbar", "Schiene", "Land"]
onlineList = {}

def save_json_file(data):
    # Output file path
    output_path = "F:\WebTools\public\list.json"

    # Write JSON object to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def read_online_list(search_path, onlineList):
    with open(r'T:\AT_Datencenter\konfigurierbare_Serien.csv', mode='r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for idx, row in enumerate(reader, start=1):
            filtered_row = {header: row.get(header, '') for header in headerList}
            onlineList[idx] = filtered_row
    
    # print(onlineList)
    find_all_json(search_path, onlineList)

def find_all_json(root_path, onlineList):
    """
    Walk through all folders starting from root_path, parse JSON files,
    """
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
                                    'online': '',
                                    'konfig':'',
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
                                    'entlasgung': data.get('settings',{}).get('entlastung', ''),
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
    
    # print(fullModelList)
    for modelId, modelEntry in fullModelList.items():
        try:
            modesIdShort = fullModelList[modelId]['fileName']
            if fullConditionsList[modesIdShort] != '':
                for innerId, conditionEntry in fullConditionsList[modesIdShort].items():
                    fullModelList[modelId]['productNumber'] = conditionEntry.get('productNo')
                    fullModelList[modelId]['productVariants'] += innerId + ' / '
                    if fullModelList[modelId]['description'] == '':
                        fullModelList[modelId]['description'] = conditionEntry.get('description')
                    for onlineId, onlineEntry in onlineList.items():
                        if onlineEntry['Artikelnummer'] != '' and onlineEntry['Artikelnummer'] in fullModelList[modelId]['productNumber'] and onlineEntry['Schiene'] == fullModelList[modelId]['brand'] and onlineEntry['Land'] == fullModelList[modelId]['locale']:
                            fullModelList[modelId]['online'] = onlineEntry['live']
                            fullModelList[modelId]['konfig'] = onlineEntry['konfigurierbar']

        except KeyError as e:
            print(f'KeyError: {e} not found in conditions.json')

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

# Example usage:
if __name__ == "__main__":
    # Set your search root path and target values here
    # search_path = (r"F:\WebTools\AktionspreisFixer\XML-Test")
    search_path = (r"C:\xxxlutz\IG-Creator\XXXLutz\ICOM")
    read_online_list(search_path, onlineList)
    # find_all_json(search_path)