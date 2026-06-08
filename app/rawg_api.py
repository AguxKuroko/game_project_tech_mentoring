import logging

import requests
from fastapi import HTTPException, status

from app.api_keys_config import get_api_keys
from app.models import RawgApiData
from app.utils import extract_genres, extract_release_year

GAME_API_URL = "https://api.rawg.io/api/games"

logger = logging.getLogger(__name__)


def rawg_api_call(year: int) -> RawgApiData | None:
    params = {
        "key": get_api_keys().RAWG_API_KEY,
        "dates": f"{year}-01-01,{year}-12-31",
        "ordering": "metacritic",
        "page_size": 1,
        "metacritic": "1,100",  # ensure metascore exists
    }
    logger.info(f"Fetching RAWG API data | year={year}", extra={"year": year, "step": "rawg_request"})
    try:
        response = requests.get(GAME_API_URL, params=params, timeout=15)
        response.raise_for_status()  # catch HTTP errors
    except requests.exceptions.RequestException:
        logger.error(f"RAWG API request failed | year={year}", extra={"year": year, "step": "rawg_error"}, exc_info=True)
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_502_BAD_GATEWAY, detail="External game API request failed."
        )

    api_raw_data = response.json()
    results = api_raw_data.get("results", [])

    if not results:
        logger.warning(f"No game data found | year={year}", extra={"year": year, "reason": "no_results"})
        return None

    game_raw = results[0]

    if not isinstance(game_raw.get("metacritic"), int):  # defense againt None from gameapi if happens
        logger.warning(f"Missing metascore in RAWG response | year={year}", extra={"year": year, "reason": "missing_metascore"})
        return None

    logger.info(f"RAWG API fetch successful | year={year}", extra={"year": year, "step": "rawg_success"})
    return RawgApiData(
        game_name=game_raw["name"],
        game_id=game_raw["id"],
        game_release_year=extract_release_year(game_raw),
        game_meta_score=game_raw["metacritic"],
        game_genre=extract_genres(game_raw["genres"]),
        game_dropped_count=game_raw.get("added_by_status", {}).get("dropped", 0),
        game_screenhosts=game_raw.get("short_screenshots", []),
    )
