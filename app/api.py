import requests
from app.api_config import api_game_key
from app.models import RawgApiData

GAME_API_URL = "https://api.rawg.io/api/games"

def rawg_api_call(year:int)->RawgApiData:
    params = {
        "key": api_game_key.RAWG_API_KEY,
        "dates": f"{year}-01-01,{year}-12-31",
        "ordering": "metacritic",
        "page_size": 1,
        "metacritic" : "1,100"  # this must be str so the filtering will work and we would not get NONE for metacritic score
    }

    response = requests.get(GAME_API_URL, params=params)

    api_raw_data = response.json()

    game_raw = api_raw_data['results'][0]


    return  RawgApiData(
                        game_name = game_raw['name'],
                        game_id = game_raw['id'],
                        game_release_year = (game_raw['released'].split("-")[0]),
                        game_meta_score = game_raw['metacritic'],
                        game_screenhosts=game_raw['short_screenshots']
    )
