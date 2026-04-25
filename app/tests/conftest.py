import pytest

from app.models import RawgApiData


@pytest.fixture
def rawg_api_fake_game():
    return RawgApiData(
        game_name="Unit test 2021",
        game_id=1,
        game_release_year="2021",
        game_meta_score=20,
        game_genre=["action", "fps"],
        game_dropped_count=777,
        game_screenhosts=[],
    )


@pytest.fixture
def fake_json_with_none_metascore():
    return {
        "results": [
            {
                "name": "Test",
                "id": 1,
                "metacritic": None,
                "released": "2020-01-01",
                "genres": [],
                "added_by_status": {},
                "short_screenshots": [],
            }
        ]
    }


@pytest.fixture
def valid_fake_json():
    return {
        "results": [
            {
                "name": "Unit test 2021",
                "id": 1,
                "metacritic": 20,
                "released": "2021-01-01",
                "genres": [{"name": "action"}, {"name": "fps"}],
                "added_by_status": {"dropped": 777},
                "short_screenshots": [],
            }
        ]
    }
