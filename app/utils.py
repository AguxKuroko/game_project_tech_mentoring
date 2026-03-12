# Helper function for LIVE game api call
def extraction_release_year(release_year_from_api: dict) -> str:
    """Function extract YEAR from full datetime str"""
    year = release_year_from_api.get("released")
    if not year:
        return "Data not provided"
    return year.split("-")[0]
