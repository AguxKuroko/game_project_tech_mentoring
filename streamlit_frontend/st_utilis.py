from datetime import datetime


def get_current_year() -> int:
    "Get current year"
    return datetime.now().year
