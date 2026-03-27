from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.responses import FileResponse

from app.meme_generator import generate_game_meme
from app.models import RawgApiData, ResponseFormat
from app.rawg_api import rawg_api_call

app = FastAPI(
    title="🎮 Worst Game Meme Generator 🎮",
    description="""Enter a year and receive a spicy, slightly unhinged meme about games that made
    players question their life choices. Results may vary… but vibes are guaranteed.""",
)


@app.get("/", include_in_schema=False)
def home():
    image_path = Path("app") / "home_endpoint_image" / "welcome.png"
    return FileResponse(image_path)


@app.get(
    "/worst_game/{year}",
    description="Get a chaotic meme or JSON about the most questionable game of the given year.",
)
def worst_game_per_year(
    request: Request,
    year: int = Path(..., description="Year of the game. Must not be in the future."),
    format: ResponseFormat = Query(default=ResponseFormat.json, description="Response format: json or image"),
):
    if year > datetime.now().year:  # if the year is in the future we do not fetch data"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{year} is in the future. No bad games have been made yet...or have they?")

    mode = request.headers.get("x-mode", "normal")

    worst_game: RawgApiData | None = rawg_api_call(year)

    if worst_game is not None:
        if format == ResponseFormat.image:
            meme = generate_game_meme(worst_game, mode)
            return FileResponse(meme)

        return worst_game  # fastapi will convert it to json

    # if year is <= current and no metacrtic -> error msg"
    return {"message": f"No game with a valid Metacritic score was found for year {year}."}
