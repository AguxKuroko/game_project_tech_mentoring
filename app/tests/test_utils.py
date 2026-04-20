import pytest

from app.utils import extract_genres, extract_release_year, prepare_images_for_openai


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
    def empty_list(self):
        data = []
        actual = prepare_images_for_openai(data)
        expected = []

        assert actual == expected
