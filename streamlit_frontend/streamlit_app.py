import streamlit as st

from streamlit_frontend.st_utilis import handle_generate, render_how_it_works, render_sidebar, render_year_input, set_config_page

set_config_page()

st.title("Worst Game Meme Generator")
st.markdown("###### *Enter a year. Receive a cursed meme about the game that made players question everything.*")

render_how_it_works()

year = render_year_input()

if st.button("Generate meme", type="primary", width="stretch"):
    handle_generate(year)


render_sidebar()
