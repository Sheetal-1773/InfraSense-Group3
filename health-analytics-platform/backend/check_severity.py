import requests
alerts = requests.get('http://localhost:8000/api/alerts').json()
print('Severity distribution:')
from collections import Counter
print(Counter(a['severity'] for a in alerts))