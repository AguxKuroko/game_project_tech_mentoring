from pathlib import Path
from unittest.mock import Mock, patch

from app.meme_generator import generate_game_meme


class TestGenerateGameMeme:
    @patch("app.meme_generator.get_api_keys")
    @patch("pathlib.Path.write_bytes")
    @patch("app.meme_generator.OpenAI")
    def test_generate_game_meme_without_screenshots_not_saving(
        self, mock_openai, mock_write_bytes, mock_keys, get_fake_api_keys, rawg_api_fake_game_without_screenshots
    ):
        mock_keys.return_value = get_fake_api_keys
        fake_result = Mock()  # result
        fake_result.data = [Mock()]
        fake_result.data[0].b64_json = "SGVsbG8="

        mock_client = Mock()  # openai mock
        mock_client.images.generate.return_value = fake_result
        mock_openai.return_value = mock_client

        result = generate_game_meme(rawg_api_fake_game_without_screenshots, "normal", False)

        assert isinstance(result, bytes)
        assert result == b"Hello"
        mock_write_bytes.assert_not_called()

    @patch("app.meme_generator.get_api_keys")
    @patch("pathlib.Path.write_bytes")
    @patch("app.meme_generator.prepare_images_for_openai")
    @patch("app.meme_generator.OpenAI")
    def test_generate_game_meme_with_screenshots(
        self, mock_openai, mock_prepare, mock_write_bytes, mock_keys, get_fake_api_keys, rawg_api_fake_game_with_screenshots
    ):
        mock_keys.return_value = get_fake_api_keys

        mock_prepare.return_value = ["img1", "img2", "img3"]

        # fake OpenAI response
        fake_result = Mock()
        fake_result.data = [Mock()]
        fake_result.data[0].b64_json = "SGVsbG8="  # base64 for "Hello"

        # mock OpenAI client
        mock_client = Mock()
        mock_client.images.edit.return_value = fake_result
        mock_openai.return_value = mock_client

        # call function
        result = generate_game_meme(rawg_api_fake_game_with_screenshots, "normal", save=True)

        assert isinstance(result, Path)

        mock_write_bytes.assert_called_once()

        # verify OpenAI was called exactly once
        mock_client.images.edit.assert_called_once()

        # verify EXACTLY 3 screenshots were passed
        call_args = mock_client.images.edit.call_args
        assert len(call_args.kwargs["image"]) == 3
