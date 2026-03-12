from datetime import datetime

from fastapi import FastAPI, HTTPException, status

from app.api import rawg_api_call
from app.models import RawgApiData

app = FastAPI()


@app.get("/", include_in_schema=False)
def home():
    return "Worst Game of ....year!"


@app.get("/worst_game/{year}")
def worst_game_per_year(year: int):
    if year > datetime.now().year:  # if the year is in the future we do not fetch data"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{year} is in the future."
        )

    worst_game: RawgApiData | None = rawg_api_call(year)

    if worst_game is not None:
        return worst_game  # fastapi will convert it to json

    # if year is <= current and no metacrtic -> error msg"
    return {"message": f"No game with a valid Metacritic score was found for year {year}."}
