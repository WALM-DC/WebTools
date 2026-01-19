import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://services.ist.lutz.gmbh/HybrisProductDelivery/clients/2/assortmentLines/0L/productNumbers/0005530110/01"

response = requests.get(url, verify=False)

print("Status:", response.status_code)
print("RAW RESPONSE (first 500 chars):")
print(response.text[:500])