from fastapi import FastAPI, HTTPException, status
from app.api import rawg_api_call
from app.models import RawgApiData
from datetime import datetime

app = FastAPI()


@app.get("/", include_in_schema=False)
def home():
    return "Worst Game of ....year!"


@app.get("/worst_game/{year}")
def worst_game_per_year(year: int):
    if year <= (datetime.now().year - 2):  # to prevent user form getting some other error and to make sure that if someone put 2027 for example then he will get the baka error"
        worst_game : RawgApiData = rawg_api_call(year)
        return {worst_game.game_name : worst_game.game_meta_score}


    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Year not found! You BAKA user!")


@app.get("/worst_game_two/{year}")
def worst_game_per_year_two(year: int):
    game_year = ...

    if game_year:
        return {year: game_year}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Year not found! You BAKA user!")
