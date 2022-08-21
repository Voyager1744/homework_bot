import requests
import time
from pprint import pprint

date = time.time() - 2629743 * 3
token = 'y0_AgAAAAAA-MvhAAYckQAAAADMu9sXGoFAqIlnS4CnWCT97HFr-TVbi5s'
url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {token}'}
payload = {'from_date': int(date)}
homework_statuses = requests.get(url, headers=headers, params=payload)
pprint(homework_statuses.json()['homeworks'][0])

three_month = 2629743*3
print(time.time())
print(date)
print(type(homework_statuses.json()['homeworks'][0]))
