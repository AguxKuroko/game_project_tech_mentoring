from unittest.mock import Mock, patch

from app.rawg_api import rawg_api_call


def create_mock_response(json_data):
    mock = Mock()
    mock.raise_for_status.return_value = None
    mock.json.return_value = json_data
    return mock


class TestRawgApiCall:
    @patch("app.rawg_api.requests.get")
    def test_rawg_api_with_empty_results(self, get_mock):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"results": []}

        get_mock.return_value = mock_response

        assert rawg_api_call(2022) is None

    @patch("app.rawg_api.requests.get")
    def test_rawg_api_invalid_metascore_returns_none(self, get_mock, fake_json_with_none_metascore):
        get_mock.return_value = create_mock_response(fake_json_with_none_metascore)
        assert rawg_api_call(2020) is None

    @patch("app.rawg_api.requests.get")
    def test_rawg_api_success(self, get_mock, rawg_api_fake_game, valid_fake_json):
        get_mock.return_value = create_mock_response(valid_fake_json)
        actual = rawg_api_call(2021)
        assert actual == rawg_api_fake_game
        assert actual.game_name == rawg_api_fake_game.game_name
