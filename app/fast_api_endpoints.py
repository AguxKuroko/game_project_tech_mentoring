import logging
from datetime import datetime

import logfire
from fastapi import Depends, FastAPI, HTTPException, Path, Query, Request, Response, status
from fastapi.responses import FileResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, select

from app.app_config import ConfigAppMode, ConfigResponseFormat, app_paths
from app.auth import verify_backend_api_key
from app.db.db_models import Meme, MemeStats, MemeTopResponse
from app.db.db_utils import get_time
from app.db.engine import get_engine
from app.logging_config import setup_logging
from app.meme_generator import generate_game_meme
from app.models import MemeGeneratorJsonData, RawgApiData
from app.rawg_api import rawg_api_call
from app.utils import clean_filename, lifespan

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="🎮 Worst Game Meme Generator 🎮",
    description="""Enter a year and receive a spicy, slightly unhinged meme about games that made
    players question their life choices. Results may vary… but vibes are guaranteed.""",
    lifespan=lifespan,
)

logfire.instrument_fastapi(app)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(app_paths.home_image)


@app.get(
    "/worst_game/{year}",
    description="Get a chaotic meme or JSON about the most questionable game of the given year.",
    dependencies=[Depends(verify_backend_api_key)],
)
def worst_game_per_year(
    request: Request,
    year: int = Path(..., description="Year for which to retrieve the worst game based on Metascore."),
    format: ConfigResponseFormat = Query(default=ConfigResponseFormat.json, description="Response format: json or image"),
):
    logger.info(f"Request received | year={year}", extra={"year": year, "endpoint": "worst_game"})
    if year > datetime.now().year:
        logger.warning(f"Invalid request | future year={year}", extra={"year": year, "reason": "future_year"})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{year} is in the future. No bad games have been made yet...or have they?")

    mode_raw: str = request.headers.get("x-mode", ConfigAppMode.normal)

    try:
        mode = ConfigAppMode(mode_raw)
    except ValueError:
        mode = ConfigAppMode.normal

    logger.info(f"Fetching RAWG data | year={year}", extra={"year": year, "step": "rawg_api"})
    worst_game: RawgApiData | None = rawg_api_call(year)

    if worst_game is None:
        logger.warning(f"No valid game found | year={year}", extra={"year": year, "reason": "no_game_found"})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No game with a valid Metacritic score was found for year {year}.")

    safe_name = clean_filename(worst_game.game_name)
    filepath = app_paths.memes_dir / f"{safe_name}_{worst_game.game_release_year}.png"

    if mode == ConfigAppMode.dog:
        logger.info("Mode activated | dog", extra={"mode": "dog"})
        image_bytes: bytes = generate_game_meme(worst_game, mode, save=False)
        return Response(content=image_bytes, media_type="image/png")

    with Session(get_engine()) as session:
        try:
            logger.info(f"Checking cache | year={year}", extra={"year": year, "step": "cache_check"})
            db_meme: Meme | None = session.exec(select(Meme).where(Meme.file_path == str(filepath))).one_or_none()

            if db_meme is None:
                logger.info(f"Cache miss | generating meme | year={year}", extra={"year": year, "step": "generate_meme"})
                generate_game_meme(worst_game, mode)
                db_meme = Meme(
                    game_name=worst_game.game_name,
                    metascore=worst_game.game_meta_score,
                    file_path=str(filepath),
                    year=worst_game.game_release_year,
                )
                session.add(db_meme)
                session.flush()  # get id without committing
                logger.info(f"Meme created | id={db_meme.id} | game={db_meme.game_name}", extra={"meme_id": db_meme.id, "game_name": db_meme.game_name})

            existing_stats: MemeStats | None = session.exec(select(MemeStats).where(MemeStats.meme_id == db_meme.id)).one_or_none()

            if existing_stats is not None:
                logger.info("Stats updated | increment access_count", extra={"step": "stats_update"})
                existing_stats.access_count += 1
                existing_stats.last_accessed = get_time()
            else:
                logger.info(f"Stats created | game={db_meme.game_name}", extra={"game_name": db_meme.game_name, "step": "stats_create"})
                db_stats = MemeStats(meme_id=db_meme.id, access_count=1, last_accessed=get_time())
                session.add(db_stats)

            session.commit()  # one commit — both meme + stats, or nothing
            logger.info(f"DB commit successful | game={db_meme.game_name}", extra={"game_name": db_meme.game_name, "step": "db_commit"})

        except SQLAlchemyError:
            session.rollback()  # undo everything if anything fails
            logger.error(
                f"DB rollback | failed to save | game={getattr(db_meme, 'game_name', 'unknown')}",
                extra={"game_name": getattr(db_meme, "game_name", None), "step": "db_error"},
                exc_info=True,
            )
            raise HTTPException(  # noqa: B904
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database operation failed."
            )

        if format == ConfigResponseFormat.image:
            return FileResponse(filepath)

        return MemeGeneratorJsonData(game_name=worst_game.game_name, game_meme=f"{request.base_url}worst_game/{year}?format=image")


@app.get(
    "/hall_of_shame",
    description="Welcome to the hall of shame. These games were memed so hard, they achieved immortality.",
    dependencies=[Depends(verify_backend_api_key)],
)
def hall_of_shame_stats(request: Request) -> list[MemeTopResponse]:
    with Session(get_engine()) as session:
        logger.info("Request received | hall_of_shame", extra={"endpoint": "hall_of_shame"})
        max_count = session.exec(select(MemeStats.access_count).order_by(MemeStats.access_count.desc())).first()

        if max_count is None:
            logger.warning("No data available | hall_of_shame", extra={"endpoint": "hall_of_shame", "reason": "no_data"})
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No memes yet. Peace has been restored... for now")

        results = session.exec(select(Meme, MemeStats).join(MemeStats, MemeStats.meme_id == Meme.id).where(MemeStats.access_count == max_count)).all()
    logger.info("Response returned | hall_of_shame top memes", extra={"endpoint": "hall_of_shame", "step": "response"})
    return [
        MemeTopResponse(
            game_name=db_meme.game_name,
            game_metascore=db_meme.metascore,
            year=db_meme.year,
            image_url=f"{request.base_url}worst_game/{db_meme.year}?format=image",
            access_count=db_stats.access_count,
        )
        for db_meme, db_stats in results
    ]
