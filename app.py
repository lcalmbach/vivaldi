import streamlit as st
from streamlit_option_menu import option_menu
from helper import get_season
import pandas as pd
from datetime import datetime, timedelta
import vivaldi_info, vivaldi_stats, vivaldi_plots, vivaldi_heatmap, vivaldi_chat
import requests
import numpy as np
import helper

parquet_file_path = "data/100254.parquet"
# https://icons.getbootstrap.com/?q=image
menu_icons = ["house", "table", "graph-up","thermometer-high", "chat-dots"]

__version__ = "0.0.7"
__author__ = "Lukas Calmbach"
__author_email__ = "lcalmbach@gmail.com"
VERSION_DATE = "2024-09-01"
APP_NAME = "Vivaldi"
GIT_REPO = "https://github.com/lcalmbach/vivaldi"
SOURCE_URL = "https://data.bs.ch/explore/dataset/100254/"

menu_options = [
    "Über die App",
    "Tabellen",
    "Zeitreihen",
    "Heatmap",
    "Meteo-Chat"
]

def get_data(parquet_file_path):
    """
    Retrieves data from a parquet file and updates it with new records from an API.
    The function verifies if the last date in the DataFrame is more than 1 day before the current date. If so, it 
    fetches new data from the API and appends it to the DataFrame.

    Args:
        parquet_file_path (str): The file path of the parquet file.

    Returns:
        pandas.DataFrame: The updated DataFrame containing the data from the parquet file.

    Raises:
        None
    """
    parquet_df = pd.read_parquet(parquet_file_path)
    last_date = parquet_df['date'].max().date()
    two_days_ago = datetime.now().date() - timedelta(days=2)

    # Check if last_date is more than 2 days before the current date
    if last_date < two_days_ago:
        last_date_str = last_date.strftime("%Y-%m-%d")

        url = f'https://data.bs.ch/api/records/1.0/search/?dataset=100254&q=date%20%3E%20%22{last_date_str}%22&rows=100&sort=date'

        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Extract the JSON data from the response
            data = response.json()
            new_df = pd.json_normalize(data['records'])
            if len(new_df) > 0:
                fields = ['fields.date', 'fields.jahr', 'fields.tre200d0', 'fields.tre200dn', 'fields.tre200dx']
                new_df = new_df[fields]
                new_df.columns = ['date','year','temperature','min_temperature', 'max_temperature']
                new_df['date'] = pd.to_datetime(new_df['date'])
                new_df = new_df.astype({'year': 'int32', 'temperature': 'float64', 'min_temperature': 'float64', 'max_temperature': 'float64'})
                new_df = new_df.sort_values(by='date')
                
                parquet_df = pd.concat([parquet_df, new_df])
                parquet_df = parquet_df.sort_values(by='date')
                parquet_df['season_year'] = parquet_df['date'].apply(lambda x: x.year + 1 if x.month == 12 else x.year)
                parquet_df = helper.add_meteorological_season(parquet_df, 'date')
                parquet_df['day_in_season'] = parquet_df.groupby(['season', 'season_year']).cumcount() + 1
                parquet_df.to_parquet(parquet_file_path)
    parquet_df['hitzetag'] = np.where(parquet_df['max_temperature'] > 30, 1, 0)
    parquet_df['eistag'] = np.where(parquet_df['max_temperature'] < 0, 1, 0)
    parquet_df['frosttag'] = np.where(parquet_df['min_temperature'] < 0, 1, 0)
    return parquet_df

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
        with st.spinner("Daten werden geladen..."):
            st.session_state.data = get_data(parquet_file_path) 
            st.session_state.years = sorted(st.session_state.data['year'].unique(), reverse=True)
            st.session_state.min_year, st.session_state.max_year = min(st.session_state.years), max(st.session_state.years)
            st.session_state.current_season = get_season(datetime.now())
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
    if index == 3:
        vivaldi_heatmap.show()
    if index == 4:
        vivaldi_chat.show()

    st.sidebar.markdown(APP_INFO, unsafe_allow_html=True)


if __name__ == "__main__":
    main()