import random
from datetime import datetime

import requests
import streamlit as st

from streamlit_frontend.content import WAITING_MESSAGES
from streamlit_frontend.st_config import frontend_paths

BACKEND_API_KEY = st.secrets["BACKEND_API_KEY"]
BACKEND_URL = st.secrets["BACKEND_URL"]


def get_current_year() -> int:
    return datetime.now().year


def set_config_page():
    return st.set_page_config(
        page_title="Worst Game Meme Generator",
        page_icon="🎮",
        layout="centered",
    )


def render_how_it_works():
    with st.expander("How this works"):
        st.markdown(
            "- :primary[**First request for a year**]: calls the OpenAI API to generate the meme — costs real money.\n"
            "- :primary[**Subsequent requests**]: served from cache, no API call.\n"
            "- :primary[**If no meme appears**]: the OpenAI funds may have perished. Refresh later, or accept fate.\n"
            "- :primary[**About the text**]: memes are AI-conjured. If the letters look haunted, that's working as intended."
        )


def render_year_input() -> int | None:
    return st.number_input(
        label="Pick a year",
        value=None,
        placeholder="e.g. 2015",
        min_value=1970,
        max_value=get_current_year(),
    )


def render_sidebar():
    with st.sidebar:
        st.markdown("### About this app")
        st.markdown("A meme generator for the worst-rated games in history. Enter a year → receive a cursed AI-generated meme.")

        st.divider()

        st.markdown("**Built by** Agnieszka")
        st.markdown("Engineered with questionable taste")
        st.link_button(
            "Check on GitHub",
            "https://github.com/AguxKuroko/worst-games-memed",
        )
        st.divider()

        st.image(frontend_paths.welcome_image, width=200)


def handle_generate(year: int | None) -> None:
    if year is None:
        st.warning("Pick a year first.")
        return

    fast_api_url = f"{BACKEND_URL}/worst_game/{year}?format=image"

    with st.spinner(random.choice(WAITING_MESSAGES)):
        try:
            response = requests.get(
                fast_api_url,
                headers={"X-BACKEND-KEY": BACKEND_API_KEY},
                timeout=180,
            )
        except requests.RequestException as e:
            st.error(f"Could not reach the meme backend: {e}")
            return

    if response.status_code == 200:
        st.image(response.content)
        return

    show_error_for_status(response, year)


def show_error_for_status(response: requests.Response, year: int) -> None:
    if response.status_code == 404:
        st.error(f"No meme to show... {year} has no game with a valid metascore.")
    elif response.status_code == 400:
        st.error(f"{year} is in the future. No bad games have been made yet... or have they?")
    elif response.status_code == 422:
        st.warning(
            f"{year}'s worst game is so cursed even the AI refused to make a meme about it. "
            f"The cosmic safety system blocked our spell. Try a different year — the meme gods may be kinder."
        )
    else:
        st.error(f"Something went horribly wrong... error {response.status_code}")
