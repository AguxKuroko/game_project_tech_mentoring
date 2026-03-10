import requests

from app.api_config import api_game_key
from app.models import RawgApiData
from app.utils import release_year_extraction

GAME_API_URL = "https://api.rawg.io/api/games"


def rawg_api_call(year: int) -> RawgApiData | None:
    params = {
        "key": api_game_key.RAWG_API_KEY,
        "dates": f"{year}-01-01,{year}-12-31",
        "ordering": "metacritic",
        "page_size": 1,
        "metacritic": "1,100",  # ensure metascore exists
    }

    response = requests.get(GAME_API_URL, params=params)
    response.raise_for_status()  # catch HTTP errors

    api_raw_data = response.json()
    results = api_raw_data.get("results", [])

    if results:
        game_raw = results[0]

        return RawgApiData(
            game_name=game_raw["name"],
            game_id=game_raw["id"],
            game_release_year=release_year_extraction(game_raw),
            game_meta_score=game_raw.get("metacritic"),
            game_screenhosts=game_raw.get("short_screenshots", []),
        )

    return None
