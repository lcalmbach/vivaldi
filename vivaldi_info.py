import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import os

from texte import txt
from helper import get_season

parquet_file_path = os.path.join('./data', '100254.parquet')


def show():
    date_min = st.session_state.data.date.min()
    date_max = st.session_state.data.date.max()
    min2max = f"{date_min.strftime('%d.%m.%Y')} bis {date_max.strftime('%d.%m.%Y')}"
    st.title("Vivaldi - Die Jahreszeiten-App") 
    st.markdown(txt['intro'].format(min2max))
    