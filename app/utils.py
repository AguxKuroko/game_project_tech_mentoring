# Helper function for LIVE game api call
def release_year_extraction(releasyear_from_api: dict) -> str:
    if releasyear_from_api["released"] is None:
        return "Data not provided"
    return releasyear_from_api["released"].split("-")[0]
