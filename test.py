from pprint import pprint
from datetime import datetime
import requests

url = ('https://newsapi.org/v2/top-headlines?country=ru&apiKey=fc730c64a9104752b13f184a6d630a83')
response = requests.get(url)
posts_api = response.json()['articles']
for i in posts_api:
    print(i['description'])
    print(i['urlToImage'])


# (datetime(int('2022-04-16T22:40:00Z'[:4]), int('2022-04-16T22:40:00Z'[5:7]), int('2022-04-16T22:40:00Z'[8:10]), int('2022-04-16T22:40:00Z'[11:13]), int('2022-04-16T22:40:00Z'[14:16])))
