import os
import json

def find_json_with_values(root_path, target_values):
    """
    Walk through all folders starting from root_path, parse JSON files,
    and print file paths that contain specified values.
    
    :param root_path: The root directory to start searching.
    :param target_values: A list or set of values to search for in JSON files.
    """
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.endswith('.json'):
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if contains_target_values(data, target_values):
                            if contains_target_keys(data, {'settings','aktion'}):
                                print(f"[MATCH] {file_path}")
                                print('\t catalog: '+data['catalog'])
                                print('\t brand: '+data['brand'])
                                print('\t productGroup: '+data['productGroup'])
                                print('\t preis: '+str(data['settings']['kaa1']))
                                print('\t entlastung: '+str(data['settings']['entlastung']))
                                print('\t aktion: '+str(data['settings']['aktion']))

                                data['settings']['aktion'] = 20

                    with open(file_path, 'w') as f:
                        json.dump(data, f)
                        
                # except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    # print(f"[ERROR] Could not parse {file_path}: {e}")
                except Exception as e:
                    print(f"[ERROR] Unexpected error with {file_path}: {e}")

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
    search_path = (r"F:\WebTools\walm.github.io\AktionspreisFixer\XML-Test")
    values_to_find = {"productGroup", "08"}

    find_json_with_values(search_path, values_to_find)