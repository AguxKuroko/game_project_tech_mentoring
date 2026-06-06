from unittest.mock import Mock, patch

import pytest
import requests
from fastapi import HTTPException

from app.rawg_api import rawg_api_call


# helper function for creating mock object
def create_mock_response(json_data):
    mock = Mock()
    mock.raise_for_status.return_value = None
    mock.json.return_value = json_data
    return mock


class TestRawgApiCall:
    @patch("app.rawg_api.get_api_keys")
    @patch("app.rawg_api.requests.get")
    def test_rawg_api_with_empty_results(self, get_mock, mock_keys, get_fake_api_keys):
        mock_keys.return_value = get_fake_api_keys
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"results": []}

        get_mock.return_value = mock_response

        assert rawg_api_call(2022) is None

    @patch("app.rawg_api.get_api_keys")
    @patch("app.rawg_api.requests.get")
    def test_rawg_api_invalid_metascore_returns_none(self, get_mock, mock_keys, get_fake_api_keys, fake_json_with_none_metascore):
        mock_keys.return_value = get_fake_api_keys
        get_mock.return_value = create_mock_response(fake_json_with_none_metascore)
        assert rawg_api_call(2020) is None

    @patch("app.rawg_api.get_api_keys")
    @patch("app.rawg_api.requests.get")
    def test_rawg_api_success(self, get_mock, mock_keys, get_fake_api_keys, rawg_api_fake_game_without_screenshots, valid_fake_json):
        mock_keys.return_value = get_fake_api_keys
        get_mock.return_value = create_mock_response(valid_fake_json)
        actual = rawg_api_call(2021)
        assert actual == rawg_api_fake_game_without_screenshots
        assert actual.game_name == rawg_api_fake_game_without_screenshots.game_name

    @patch("app.rawg_api.get_api_keys")
    @patch("app.rawg_api.requests.get")
    def test_request_error(self, get_mock, mock_keys, get_fake_api_keys):
        mock_keys.return_value = get_fake_api_keys
        get_mock.side_effect = requests.exceptions.RequestException()

        with pytest.raises(HTTPException):
            rawg_api_call(1988)

    @patch("app.rawg_api.get_api_keys")
    @patch("app.rawg_api.requests.get")
    def test_raise_for_status_error(self, get_mock, mock_keys, get_fake_api_keys):
        mock_keys.return_value = get_fake_api_keys
        mock_response = Mock()

        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        get_mock.return_value = mock_response

        with pytest.raises(HTTPException):
            rawg_api_call(2022)
