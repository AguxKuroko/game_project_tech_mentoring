from fastapi import FastAPI, HTTPException, status

fake_data = {2020: "Diablo", 2021: "Pokemon S", 2022: "Destiny"}

app = FastAPI()


@app.get("/", include_in_schema=False)
def home():
    return "Worst Game of ....year!"


@app.get("/worst_game/{year}")
def worst_game_per_year(year: int):
    if year in fake_data.keys():
        return {year: fake_data[year]}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Year not found! You BAKA user!")


@app.get("/worst_game_two/{year}")
def worst_game_per_year_two(year: int):
    game_year = fake_data.get(year)

    if game_year:
        return {year: game_year}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Year not found! You BAKA user!")
