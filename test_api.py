import json
import requests

files = {'pdf_file': open('reports/Reports(1).pdf', 'rb')}
url = 'http://127.0.0.1:8000/extract_object'

response = requests.post(url, files=files)

if response.status_code == 200:
    data = json.loads(response.text)
    if 'error' in data:
        print(data['error'])
    else:
        print(json.dumps(data['score'], indent=4))
else:
    print(f"Failed with status code {response.status_code}")
