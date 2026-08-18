import requests
alerts = requests.get('http://localhost:8000/api/alerts').json()
print('Type x Status:')
for a in alerts[:10]:
    print(f'  {a["alert_type"]} - {a["status"]}')