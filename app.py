import streamlit as st
from streamlit_option_menu import option_menu
from vivaldi import Vivaldi

# https://icons.getbootstrap.com/?q=image
menu_icons = ["house", "table", "graph-up", "chat-dots"]

__version__ = "0.2.3"
__author__ = "Lukas Calmbach"
__author_email__ = "lcalmbach@gmail.com"
VERSION_DATE = "2024-11-22"
APP_NAME = "Vivaldi"
GIT_REPO = "https://github.com/lcalmbach/vivaldi"
SOURCE_URL = "https://data.bs.ch/explore/dataset/100254/"

menu_options = ["Über die App", "Tabellen", "Zeitreihen", "Meteo-Chat"]

APP_INFO = f"""<div style="background-color:#34282C; padding: 10px;border-radius: 15px; border:solid 1px white;">
    <small>App von <a href="mailto:{__author_email__}">{__author__}</a><br>
    Version: {__version__} ({VERSION_DATE})<br>
    Quelle: <a href="{SOURCE_URL}">data.bs</a><br>
    <a href="{GIT_REPO}">git-repo</a></small></div>
    """


def init():
    st.set_page_config(
        page_title="Vivaldi",
        page_icon="🎻",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def main():
    init()
    if "vivaldi" not in st.session_state:
        with st.spinner("Daten werden geladen..."):
            st.session_state.vivaldi = Vivaldi()
    vivaldi = st.session_state.vivaldi
    with st.sidebar:
        st.sidebar.title("Vivaldi ☃️ 🌷 🌞 🍁")
        menu_action = option_menu(
            None,
            menu_options,
            icons=menu_icons,
            menu_icon="cast",
            default_index=0,
        )
    index = menu_options.index(menu_action)
    if index == 0:
        vivaldi.show_info()
    if index == 1:
        vivaldi.show_stats()
    if index == 2:
        vivaldi.show_plots()
    if index == 3:
        vivaldi.show_chat()

    st.sidebar.markdown(APP_INFO, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
