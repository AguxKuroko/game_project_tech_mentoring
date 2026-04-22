from io import BytesIO
from unittest.mock import Mock, patch

import pytest
import requests
from fastapi import HTTPException

from app.models import RawgApiData
from app.utils import build_prompt, clean_filename, extract_genres, extract_release_year, prepare_images_for_openai


class TestExtractReleaseYear:
    @pytest.mark.parametrize(
        "input_data, expected",
        [
            pytest.param({"released": "2021-12-01"}, "2021", id="valid string date"),
            pytest.param({"game": "Test"}, "Data not provided", id="missing key"),
            pytest.param({"released": 0}, "Data not provided", id="zero value"),
            pytest.param({"released": 2022}, "2022", id="int year"),
            pytest.param({"released": ""}, "Data not provided", id="empty string"),
            pytest.param({"released": ["2021-01-01"]}, "Data not provided", id="list"),
        ],
    )
    def test_extract_release_year(self, input_data, expected):
        assert extract_release_year(input_data) == expected


class TestExtractGenres:
    def test_dict_with_genres(self):
        data = [{"name": "action"}, {"name": "fantasy"}]
        actual = extract_genres(data)
        expected = ["action", "fantasy"]

        assert actual == expected

    def test_dict_without_genres(self):
        data = [{"released": "2021-12-01"}]
        actual = extract_genres(data)
        expected = []

        assert actual == expected

    def test_none_name(self):
        data = [{"name": None}]
        actual = extract_genres(data)
        expected = []

        assert actual == expected


class TestPrepareImagesForOpenAi:
    def test_empty_list(self):
        data = []
        actual = prepare_images_for_openai(data)
        expected = []

        assert actual == expected


class TestPrepareImagesForOpenAiMock:
    @patch("app.utils.requests.get")
    def test_prepare_image_requests(self, requests_mock):
        mock_response = Mock(spec=requests.Response)
        mock_response.content = b"fake image bytes"

        requests_mock.return_value = mock_response

        screenshot = ["http://test.com/image.jpg", "http://test.com/image_two.jpg"]

        result = prepare_images_for_openai(screenshot)

        assert len(result) == 2
        assert isinstance(result[0], BytesIO)
        assert result[1].name == "image_1.jpg"

    @patch("app.utils.requests.get")
    def test_download_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException

        with pytest.raises(HTTPException):
            prepare_images_for_openai(["http://bad-url"])


@pytest.fixture
def rawg_api_fake_game():
    return RawgApiData(
        game_name="Unit test 2025",
        game_id=1,
        game_release_year="2021",
        game_meta_score=20,
        game_genre=["action", "fps"],
        game_dropped_count=777,
        game_screenhosts=[],
    )


class TestBuildPrompt:
    def test_normal_mode(self, rawg_api_fake_game):
        result = build_prompt(rawg_api_fake_game, "normal")

        assert "Unit test 2025" in result
        assert "2021" in result

    def test_dog_mode(self, rawg_api_fake_game):
        result = build_prompt(rawg_api_fake_game, "dog")

        assert "Secret 'DOG' mode" in result
        assert "action" in result


class TestCleanFilename:
    def test_remove_special_chars():
        assert clean_filename("game@#2021!") == "game2021"

    def test_spaces_to_underscore():
        assert clean_filename("my game name") == "my_game_name"

    def test_strip_spaces():
        assert clean_filename("  test game  ") == "test_game"
