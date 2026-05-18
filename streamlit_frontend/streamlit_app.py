import streamlit as st

from app.app_config import app_paths

st.set_page_config(
    page_title="Worst Game Meme Generator",
    page_icon="🎮",
    layout="centered",
)


st.title("Worst Game Meme Generator")
st.markdown("###### *Enter a year. Receive a cursed meme about the game that made players question everything.*")
with st.expander("How this works"):
    st.markdown(
        "- **First request for a year**: calls the OpenAI API to generate the meme — costs real money.\n"
        "- **Subsequent requests**: served from cache, no API call.\n"
        "- **If no meme appears**: the OpenAI funds may have perished. Refresh later, or accept fate."
    )

year = st.number_input(
    label="Pick a year",
    value=None,
    placeholder="e.g. 2015",
    min_value=1970,
    max_value=2026,
)

with st.sidebar:
    st.markdown("### About this app")
    st.markdown("A meme generator for the worst-rated games in history. " "Enter a year → receive a cursed AI-generated meme.")

    st.divider()

    st.markdown("**Built by** Agnieszka")
    st.markdown("Engineered with questionable taste")
    st.link_button(
        "View on GitHub",
        "https://github.com/AguxKuroko/game_project_tech_mentoring",
    )
    st.divider()

    st.image(app_paths.home_image, width=200)
