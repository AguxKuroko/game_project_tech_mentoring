from pathlib import Path
from unittest.mock import Mock, patch

from app.meme_generator import generate_game_meme


class TestGenerateGameMeme:
    @patch("app.meme_generator.OpenAI")
    def test_generate_game_meme_without_screenshots_not_saving(self, mock_openai, rawg_api_fake_game_without_screenshots):
        fake_result = Mock()  # result
        fake_result.data = [Mock()]
        fake_result.data[0].b64_json = "SGVsbG8="

        mock_client = Mock()  # openai mock
        mock_client.images.generate.return_value = fake_result
        mock_openai.return_value = mock_client

        result = generate_game_meme(rawg_api_fake_game_without_screenshots, "normal", False)

        assert isinstance(result, bytes)
        assert result == b"Hello"

    @patch("app.meme_generator.prepare_images_for_openai")
    @patch("app.meme_generator.OpenAI")
    def test_generate_game_meme_with_screenshots(self, mock_openai, mock_prepare, rawg_api_fake_game_with_screenshots):
        # 1. Mock image preparation (so we don't run real logic)
        mock_prepare.return_value = ["fake_image"]

        # 2. Fake OpenAI response
        fake_result = Mock()
        fake_result.data = [Mock()]
        fake_result.data[0].b64_json = "SGVsbG8="  # base64 for "Hello"

        # 3. Mock OpenAI client
        mock_client = Mock()
        mock_client.images.edit.return_value = fake_result
        mock_openai.return_value = mock_client

        # 4. Call function
        result = generate_game_meme(rawg_api_fake_game_with_screenshots, "normal", save=True)

        # 5. Assert
        assert isinstance(result, Path)
