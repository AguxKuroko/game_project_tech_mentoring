from app.utils import clean_filename


class TestCleanFilename:
    def test_removes_special_characters(self):
        assert clean_filename("SupaCool*:TheSequel!!?@") == "SupaCoolTheSequel"
