from datetime import datetime

from fastapi import FastAPI, HTTPException, Path, Query, Request, Response, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.app_config import ConfigResponseFormat, app_paths
from app.db.db_models import Meme, MemeStats
from app.db.db_utils import get_time
from app.db.engine import engine
from app.meme_generator import generate_game_meme
from app.models import MemeGeneratorJsonData, RawgApiData
from app.rawg_api import rawg_api_call
from app.utils import clean_filename, lifespam

app = FastAPI(
    title="🎮 Worst Game Meme Generator 🎮",
    description="""Enter a year and receive a spicy, slightly unhinged meme about games that made
    players question their life choices. Results may vary… but vibes are guaranteed.""",
    lifespan=lifespam,
)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(app_paths.home_dir)


@app.get(
    "/worst_game/{year}",
    description="Get a chaotic meme or JSON about the most questionable game of the given year.",
)
def worst_game_per_year(
    request: Request,
    year: int = Path(..., description="Year for which to retrieve the worst game based on Metascore."),
    format: ConfigResponseFormat = Query(default=ConfigResponseFormat.json, description="Response format: json or image"),
):
    if year > datetime.now().year:  # if the year is in the future we do not fetch data"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{year} is in the future. No bad games have been made yet...or have they?")

    mode = request.headers.get("x-mode", "normal")

    worst_game: RawgApiData | None = rawg_api_call(year)

    if worst_game is not None:
        safe_name = clean_filename(worst_game.game_name)
        filepath = app_paths.memes_dir / f"{safe_name}_{worst_game.game_release_year}.png"

        if mode == "dog":
            image_bytes = generate_game_meme(worst_game, mode, save=False)
            return Response(content=image_bytes, media_type="image/png")

        if not filepath.exists():
            generate_game_meme(worst_game, mode)

    with Session(engine) as session:
        db_meme = session.exec(select(Meme).where(Meme.file_path == str(filepath))).first()

        if db_meme is None:
            db_meme = Meme(
                game_name=worst_game.game_name,
                file_path=str(filepath),
                year=worst_game.game_release_year,
            )
            session.add(db_meme)
            session.commit()
            session.refresh(db_meme)

    # stats session
    with Session(engine) as db_session2:
        existing_stats = db_session2.exec(select(MemeStats).where(MemeStats.meme_id == db_meme.id)).first()

        if existing_stats is not None:
            existing_stats.access_count += 1
            existing_stats.last_accessed = get_time()
            db_session2.commit()
        else:
            db_stats = MemeStats(meme_id=db_meme.id, access_count=1, last_accessed=get_time())
            db_session2.add(db_stats)
            db_session2.commit()

        if format == ConfigResponseFormat.image:
            return FileResponse(filepath)

        return MemeGeneratorJsonData(game_name=worst_game.game_name, game_meme=f"{request.base_url}worst_game/{year}?format=image")

    # if year is <= current and no metacrtic -> error msg"
    return {"message": f"No game with a valid Metacritic score was found for year {year}."}
