import os
import json
import time
import datetime
import csv
import os

# Get todays date
today = datetime.datetime.now()

# List of column headers we need to extract
headerList = ["Aktion", "vonDatum", "bisDatum", "NachlassinProzent", "Warengruppe_Kombi", "AusnahmeWarengruppe", "StatKZ_Kombi", "Marken", "ausmark", "AusnahmeLieferant"]
MKSAKTobject = {}
prodGroups = []
ausLieferanten = []
maxDiscount = 0

def num(s):
    if s == '':
        return 0
    try:
        return int(s)
    except ValueError:
        return float(s)

def filter_and_save_modellist(fullModelList, prodGroups, ausLieferanten, maxDiscount):

    addDiscountList = {}
    removeDiscountList = {}

    for idx, model in fullModelList.items():
        liefNumb = model['productNumber'][2:6]
        # filters model jsons based on the current entlasting, active discount and if the lieferantennummer isn't excluded within the desired product group
        # this can be directly used to update all files accordingly but the log files should still be written to ensure we know what was changed

        # print(model['fileName'], model['entlastung'], model['aktion'], liefNumb)
        if model["productGroup"] in prodGroups and num(model['entlastung']) < num(maxDiscount) and num(model['aktion']) < num(maxDiscount) and liefNumb not in ausLieferanten:
            addDiscountList[idx] = model
        elif num(model['aktion']) > 0:
            removeDiscountList[idx] = model

    # Output file path for log
    basePath = r"F:\WebTools\AktionspreisFixer"
    addPath = time.strftime("%Y%m%d-%H%M%S")+"_addDiscountList.json"
    removePath = time.strftime("%Y%m%d-%H%M%S")+"_removeDiscountList.json"
    output_path_add = os.path.join(basePath, addPath)
    output_path_remove = os.path.join(basePath, removePath)
    # output_path_add = (f"{basePath}\{addPath}.json")
    # output_path_remove = (f"{basePath}\{removePath}.json")

    # Write JSON object to file
    with open(output_path_add, 'w', encoding='utf-8') as f:
        json.dump(addDiscountList, f, indent=2, ensure_ascii=False)
    with open(output_path_remove, 'w', encoding='utf-8') as f:
        json.dump(removeDiscountList, f, indent=2, ensure_ascii=False)
    
    # needs calculation from entlastung and aktion to get correct percentage
    # needs final price preview file??

    # data['settings']['aktion'] = 20

# Collects 3D model data, filters by Warengruppen, Lieferanten ausnahmen and highest discount value
def find_json_with_values(root_path, prodGroups, ausLieferanten, maxDiscount):

    # print(prodGroups)
    # print(ausLieferanten)
    # print(maxDiscount)

    fullModelList = {}
    fullConditionsList = {}
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.endswith('.json') and filename.find(' ')==-1:
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if contains_target_keys(data, {'catalog'}):
                            model_object = {
                                data['catalog'].split('.')[0] +'.'+ filename.split('.')[0]: {
                                    'filePath': f'{file_path}',
                                    'fileName': filename.split('.')[0],
                                    'productNumber': '',
                                    'locale': filename.split('@')[1].split('.')[0],
                                    'brand': data.get('brand', ''),
                                    'brandName': data.get('brandName', ''),
                                    'productGroup': data.get('productGroup', ''),
                                    'kaa1': data.get('settings',{}).get('kaa1', ''),
                                    'entlastung': data.get('settings',{}).get('entlastung', ''),
                                    'aktion': data.get('settings',{}).get('aktion', ''),
                                    'pricing': data.get('settings', {}).get('pricing', '')
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
                
        except KeyError as e:
            print(f'KeyError: {e} not found in conditions!')
    
    filter_and_save_modellist(fullModelList, prodGroups, ausLieferanten, maxDiscount)

# function to establish filters for productgroup, deliveryexclusion and highestdiscount
def extended_filters(root_path, prodGroups, ausLieferanten, maxDiscount):
    for idx, object in MKSAKTobject.items():
        split_listWG = object["Warengruppe_Kombi"].split('/')
        prod_listWG = prodGroups
        prodGroups += sorted(x for x in split_listWG if x not in set(prod_listWG))

        split_listLF = object["AusnahmeLieferant"].split('/')
        prod_listLF = ausLieferanten
        ausLieferanten += sorted(x for x in split_listLF if x not in set(prod_listLF))

        if int(object["NachlassinProzent"]) > maxDiscount:
            maxDiscount = int(object["NachlassinProzent"])

    find_json_with_values(root_path, prodGroups, ausLieferanten, maxDiscount)

# checks if specific values are within the csv
def contains_target_values(data, target_values):
    if isinstance(data, dict):
        return any(contains_target_values(v, target_values) for v in data.values())
    elif isinstance(data, list):
        return any(contains_target_values(item, target_values) for item in data)
    else:
        return data in target_values

 # checks if specific keys are within the csv   
def contains_target_keys(data, target_keys):
    if isinstance(data, dict):
        for key, value in data.items():
            if key in target_keys:
                return True
            if contains_target_keys(value, target_keys):
                return True
    elif isinstance(data, list):
        return any(contains_target_keys(item, target_keys) for item in data)
    return False

# Reads MKSAKT file and convert to object
def read_csv_file(root_path, prodGroups):
    with open(r'F:\WebTools\AktionspreisFixer\MKSAKT_1_test.csv', mode='r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for idx, row in enumerate(reader, start=1):
            if "1/4/" in f"{row}":
                filtered_row = {header: row.get(header, '') for header in headerList}
                startDate = datetime.datetime.strptime(filtered_row["vonDatum"], '%d.%m.%Y')
                endDate = datetime.datetime.strptime(filtered_row["bisDatum"], '%d.%m.%Y')
                if startDate <= today and endDate >= today:
                    MKSAKTobject[idx] = filtered_row

    # from pprint import pprint
    # pprint(dict(list(MKSAKTobject.items())[:3]))
    extended_filters(root_path, prodGroups, ausLieferanten, maxDiscount)

# get going
if __name__ == "__main__":
    # Test URL
    # root_path = (r"F:\WebTools\AktionspreisFixer\XML-Test")
    # Prod URL
    root_path = (r"C:\xxxlutz\IG-Creator\XXXLutz\ICOM")
    read_csv_file(root_path, prodGroups)