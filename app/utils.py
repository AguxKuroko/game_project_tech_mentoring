from io import BytesIO

import requests
from fastapi import HTTPException, status


def extract_release_year(release_year_from_api: dict) -> str:
    """Function extract YEAR from full datetime str"""
    year = release_year_from_api.get("released")
    if not year:
        return "Data not provided"
    return year.split("-")[0]


def extract_genres(genres: list[dict]) -> list[str]:
    """Extract all genre names for the worst game of a given year."""
    return [genre["name"] for genre in genres]  # if no values in a list we will get an empty list


def extract_screenshots(screenshots_raw: list[dict]) -> list[str]:
    """Extract and normalize valid screenshot URLs for the meme generator."""
    return [image for screenshot in screenshots_raw if (image := screenshot.get("image"))]


def prepare_images_for_openai(screenshots: list[str]) -> list[BytesIO]:
    """Fetch images from URLs and transform them into BytesIO objects compatible with OpenAI API."""
    image_files = []

    for number, url in enumerate(screenshots[:3]):
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            raise HTTPException(  # noqa: B904
                status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to download screenshot: {url}"
            )

        img = BytesIO(response.content)
        img.name = f"image_{number}.jpg"

        image_files.append(img)

    return image_files
