import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

from texte import txt

parquet_file_path = "data/100254.parquet"
from helper import get_season


@st.cache_data
def get_data(parquet_file_path):
    df = pd.read_parquet(parquet_file_path)
    return df


def show():
    st.title("Vivaldi - Die Jahreszeiten-App") 
    st.markdown(txt['intro'])
    