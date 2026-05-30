import random

import requests
import streamlit as st

from app.app_config import app_paths
from streamlit_frontend.content import WAITING_MESSAGES

BACKEND_API_KEY = st.secrets["BACKEND_API_KEY"]


st.set_page_config(
    page_title="Worst Game Meme Generator",
    page_icon="🎮",
    layout="centered",
)


st.title("Worst Game Meme Generator")
st.markdown("###### *Enter a year. Receive a cursed meme about the game that made players question everything.*")
with st.expander("How this works"):
    st.markdown(
        "- :primary[**First request for a year**]: calls the OpenAI API to generate the meme — costs real money.\n"
        "- :primary[**Subsequent requests**]: served from cache, no API call.\n"
        "- :primary[**If no meme appears**]: the OpenAI funds may have perished. Refresh later, or accept fate.\n"
        "- :primary[**About the text**]: memes are AI-conjured. If the letters look haunted, that's working as intended."
    )

year = st.number_input(
    label="Pick a year",
    value=None,
    placeholder="e.g. 2015",
    min_value=1970,
    max_value=2026,
)

if st.button("Generate meme", type="primary", width="stretch"):
    if year is None:
        st.warning("Pick a year first.")
    else:
        fast_api_url = f"http://localhost:8000/worst_game/{year}?format=image"

        with st.spinner(random.choice(WAITING_MESSAGES)):
            response = requests.get(
                fast_api_url,
                headers={"X-BACKEND-KEY": BACKEND_API_KEY},
            )

        if response.status_code == 200:
            st.image(response.content)

        elif response.status_code == 404:
            st.error(f"No meme to show... {year} has no game with a valid metascore.")

        elif response.status_code == 400:
            st.error(f"{year} is in the future. No bad games have been made yet... or have they?")

        else:
            st.error(f"Something went horribly wrong... error {response.status_code}")


with st.sidebar:
    st.markdown("### About this app")
    st.markdown("A meme generator for the worst-rated games in history. Enter a year → receive a cursed AI-generated meme.")

    st.divider()

    st.markdown("**Built by** Agnieszka")
    st.markdown("Engineered with questionable taste")
    st.link_button(
        "View on GitHub",
        "https://github.com/AguxKuroko/game_project_tech_mentoring",
    )
    st.divider()

    st.image(app_paths.home_image, width=200)
