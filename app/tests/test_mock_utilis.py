from io import BytesIO
from unittest.mock import Mock, patch

import pytest
import requests
from fastapi import HTTPException

from app.utils import prepare_images_for_openai


class TestPrepareImagesForOpenAiMock:
    @patch("app.utils.requests.get")
    def test_prepare_image_requests(self, requests_mock):
        mock_respone = Mock(spec=requests.Response)
        mock_respone.content = b"fake image bytes"

        requests_mock.return_value = mock_respone

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
