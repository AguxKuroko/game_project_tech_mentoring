import pytest

from app.utils import extract_release_year


class Test:
    def test_dict_with_str_date(self):
        data = {"released": "2021-12-01"}
        actual = extract_release_year(data)
        expected = "2021"

        assert actual == expected


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
