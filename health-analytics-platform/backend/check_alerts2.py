import requests
alerts = requests.get('http://localhost:8000/api/alerts').json()
print(f'Total alerts: {len(alerts)}')
print(f'Open: {sum(1 for a in alerts if a["status"] == "open")}')
print(f'Acknowledged: {sum(1 for a in alerts if a["status"] == "acknowledged")}')
print(f'Resolved: {sum(1 for a in alerts if a["status"] == "resolved")}')
print(f'Active (open+ack): {sum(1 for a in alerts if a["status"] in ["open", "acknowledged"])}')
print()
print('Sample alert:', alerts[0] if alerts else 'None')