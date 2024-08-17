import streamlit as st
from streamlit_option_menu import option_menu
from helper import get_season
import pandas as pd
from datetime import datetime
import vivaldi_info, vivaldi_stats, vivaldi_plots

parquet_file_path = "data/100254.parquet"
# https://icons.getbootstrap.com/?q=image
menu_icons = ["house", "table", "graph-up"]

__version__ = "0.0.1"
__author__ = "Lukas Calmbach"
__author_email__ = "lcalmbach@gmail.com"
VERSION_DATE = "2023-02-01"
APP_NAME = "Vivaldi"
GIT_REPO = "https://github.com/lcalmbach/vivaldi"
SOURCE_URL = "https://data.bs.ch/explore/dataset/100254/"

menu_options = [
    "Über die App",
    "Tabellen",
    "Grafiken"
]


@st.cache_data
def get_data(parquet_file_path):
    df = pd.read_parquet(parquet_file_path)
    return df

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
    if 'data' not in st.session_state:
        st.session_state.data = get_data(parquet_file_path) 
        st.session_state.years = sorted(st.session_state.data['year'].unique(), reverse=True)
        st.session_state.min_year, st.session_state.max_year = min(st.session_state.years), max(st.session_state.years)
        st.session_state.current_season = get_season(datetime.now())
        print(st.session_state.current_season)
    with st.sidebar:
        st.sidebar.title("Vivaldi 🎻")
        menu_action = option_menu(
            None,
            menu_options,
            icons=menu_icons,
            menu_icon="cast",
            default_index=0,
        )
    index = menu_options.index(menu_action)
    if index == 0:
        vivaldi_info.show()
    if index == 1:
        vivaldi_stats.show()
    if index == 2:
        vivaldi_plots.show()

    st.sidebar.markdown(APP_INFO, unsafe_allow_html=True)


if __name__ == "__main__":
    main()