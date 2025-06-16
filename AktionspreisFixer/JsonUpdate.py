import os
import json
import datetime
import csv

# Get todays date
today = datetime.datetime.now()
dateToday = today.strftime('%d.%m.%Y')
checkDate = datetime.datetime(2025, 6, 3).strftime('%d.%m.%Y')

# List of column headers we need to extract
headerList = ["Aktion", "vonDatum", "bisDatum", "NachlassinProzent", "Warengruppe_Kombi", "AusnahmeWarengruppe", "StatKZ_Kombi", "Marken", "ausmark", "AusnahmeLieferant"]
MKSAKTobject = {}
prodGroups = []

# if dateToday >= checkDate:
#     print('Today is >=')
#     print(dateToday)
# else:
#     print('CheckDate is <')
#     print(checkDate)

def save_json_file(data):
    # Output file path for log
    # requires datestamp
    output_path = (r"F:\WebTools\AktionspreisFixer\testFilterList.json")

    # Write JSON object to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # data['settings']['aktion'] = 20

# Collects 3D model data
def find_json_with_values(root_path, prodGroups):
    """
    Walk through all folders starting from root_path, parse JSON files,
    """
    # filterList = {}
    fullModelList = {}
    fullConditionsList = {}

    # try:
    #     with open(filter_path, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         filterList = data
    #         print(filterList.get('Rabatt', {}).get('Prozent'))
    # except Exception as e:
    #     print(f"[ERROR] Unexpected error with {filter_path}: {e}")
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.endswith('.json') and filename.find(' ')==-1:
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # if model.entlastung < submitted aktion & if model.criteria fit:
                        if contains_target_keys(data, {'catalog'}):
                            if data["productGroup"] in prodGroups:
                                model_object = {
                                    data['catalog'].split('.')[0] +'.'+ filename.split('.')[0]: {
                                        'filePath': f'{file_path}',
                                        'fileName': filename.split('.')[0],
                                        'productNumber': '',
                                        'locale': filename.split('@')[1].split('.')[0],
                                        'brand': data.get('brand', ''),
                                        'brandName': data.get('brandName', ''),
                                        'productGroup': data.get('productGroup', ''),
                                        'settings': {
                                            'preis': data.get('settings',{}).get('kaa1', ''),
                                            'entlasgung': data.get('settings',{}).get('entlastung', ''),
                                            'aktion': data.get('settings',{}).get('aktion', ''),
                                            'pricing': data.get('settings', {}).get('pricing', '')
                                        }
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
                
        except KeyError as e:
            print(f'KeyError: {e} not found in conditions!')
    
    save_json_file(fullModelList)
# Loop through 3D models, check against MKSAKT object and date
# Overwrite fitting 3D models

def filter_models_byProdGroup(root_path, prodGroups):
    for group in MKSAKTobject["Warengruppe_Kombi"]:
        if not prodGroups:
            prodGroups = group.split('/')
        else:
            split_list = group.split('/')
            prod_list = prodGroups
            prodGroups += sorted(x for x in split_list if x not in set(prod_list))

    find_json_with_values(root_path, prodGroups)

# Reads MKSAKT file and convert to object
def read_csv_file(root_path, prodGroups):
    headerIndex = []
    csvRead = {}
    with open(r'F:\WebTools\AktionspreisFixer\MKSAKT_1_test.csv', mode='r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for idx, row in enumerate(reader, start=1):
            if "1/4/" in f"{row}":
                filtered_row = {header: row.get(header, '') for header in headerList}
                MKSAKTobject[idx] = filtered_row

    from pprint import pprint
    pprint(dict(list(MKSAKTobject.items())[:3]))
    # filter_models_byProdGroup(root_path, prodGroups)


# Build logic to find models to update - loop through object line by line
#   - Check valid date range
#       - Check against excluded product groups, brand & deliverers
#   - Produce preview output list

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

    root_path = (r"F:\WebTools\AktionspreisFixer\XML-Test")
    filter_path = (r"F:\WebTools\AktionspreisFixer\filter.json")

    read_csv_file(root_path, prodGroups)
    # find_json_with_values(search_path, filter_path)