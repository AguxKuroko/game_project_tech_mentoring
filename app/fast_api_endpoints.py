from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import FileResponse

from app.models import RawgApiData
from app.rawg_api import rawg_api_call

app = FastAPI()


@app.get("/", include_in_schema=False)
def home():
    image_path = Path("app") / "home_endpoint_image" / "welcome.png"
    return FileResponse(image_path)


@app.get("/worst_game/{year}")
def worst_game_per_year(year: int, request: Request):
    if year > datetime.now().year:  # if the year is in the future we do not fetch data"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{year} is in the future."
        )

    worst_game: RawgApiData | None = rawg_api_call(year)

    if worst_game is not None:
        # if request.headers.get("x-secret") == "chaos":  # easter egg for more crazy memes

        return worst_game  # fastapi will convert it to json

    # if year is <= current and no metacrtic -> error msg"
    return {"message": f"No game with a valid Metacritic score was found for year {year}."}
