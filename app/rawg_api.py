import requests
from fastapi import HTTPException, status

from app.api_keys_config import api_game_key
from app.models import RawgApiData
from app.utils import extract_genres, extraction_release_year

GAME_API_URL = "https://api.rawg.io/api/games"


def rawg_api_call(year: int) -> RawgApiData | None:
    params = {
        "key": api_game_key.RAWG_API_KEY,
        "dates": f"{year}-01-01,{year}-12-31",
        "ordering": "metacritic",
        "page_size": 1,
        "metacritic": "1,100",  # ensure metascore exists
    }

    try:
        response = requests.get(GAME_API_URL, params=params)
        response.raise_for_status()  # catch HTTP errors
    except requests.exceptions.RequestException:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_502_BAD_GATEWAY, detail="External game API request failed."
        )

    api_raw_data = response.json()
    results = api_raw_data.get("results", [])

    if not results:
        return None

    game_raw = results[0]

    if not isinstance(
        game_raw.get("metacritic"), int
    ):  # defense againt None from gameapi if happens
        return None

    return RawgApiData(
        game_name=game_raw["name"],
        game_id=game_raw["id"],
        game_release_year=extraction_release_year(game_raw),
        game_meta_score=game_raw["metacritic"],
        game_genre=extract_genres(game_raw["genres"]),
        game_dropped_count=game_raw.get("added_by_status", {}).get("dropped", 0),
        game_screenhosts=game_raw.get("short_screenshots", []),
    )
