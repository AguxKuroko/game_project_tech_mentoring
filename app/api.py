import requests
from api_config import api_game_key

year = 2021
url = "https://api.rawg.io/api/games"

params = {
        "key": api_game_key.RAWG_API_KEY,
        "dates": f"{year}-01-01,{year}-12-31",
        "ordering": "metacritic",
        "page_size": 1,
        "metacritic" : "1,100"
    }

response = requests.get(url, params=params)

api_raw_data = response.json()
print(api_raw_data)

count = 0
for game in api_raw_data['results']:
    if game['metacritic'] is not None:
        print(game['name'],game['released'],game['metacritic'],game['short_screenshots'], game['id'])
        print("")

    else:
        print(game['metacritic'] )
        count+=1
print(count)
