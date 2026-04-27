from io import BytesIO
from unittest.mock import Mock, patch

import pytest
import requests
from fastapi import HTTPException

from app.utils import build_prompt, clean_filename, extract_genres, extract_release_year, generate_meme_without_images, prepare_images_for_openai


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
        mock_get.side_effect = requests.exceptions.RequestException()

        with pytest.raises(HTTPException):
            prepare_images_for_openai(["http://bad-url"])


class TestBuildPrompt:
    def test_normal_mode(self, rawg_api_fake_game_with_screenshots):
        result = build_prompt(rawg_api_fake_game_with_screenshots, "normal")

        assert "Unit test 2021" in result
        assert "2021" in result

    def test_dog_mode(self, rawg_api_fake_game_with_screenshots):
        result = build_prompt(rawg_api_fake_game_with_screenshots, "dog")

        assert "Secret 'DOG' mode" in result
        assert "action" in result


class TestCleanFilename:
    def test_remove_special_chars(self):
        assert clean_filename("game@#2021!") == "game2021"

    def test_spaces_to_underscore(self):
        assert clean_filename("my game name") == "my_game_name"

    def test_strip_spaces(self):
        assert clean_filename("  test game  ") == "test_game"


class TestGenerateMemeWithoutImages:
    def test_generate_meme_without_images_success(self, rawg_api_fake_game_without_screenshots):
        mock_client = Mock()
        expected = {"image": "fake"}
        mock_client.images.generate.return_value = expected
        result = generate_meme_without_images(rawg_api_fake_game_without_screenshots, "normal", mock_client)
        assert result == expected

    def test_generate_meme_wihtou_images_failure(self, rawg_api_fake_game_without_screenshots):
        mock_client = Mock()

        mock_client.images.generate.side_effect = Exception("boom")

        with pytest.raises(HTTPException):
            generate_meme_without_images(rawg_api_fake_game_without_screenshots, "normal", mock_client)
