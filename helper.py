import pandas as pd
from datetime import datetime, timedelta
import socket
import os
import streamlit as st

season_name = {1:'Winter', 2:'Frühling', 3:'Sommer', 4:'Herbst'}
LOCAL_HOST = 'gladiator'

def get_current_season():
    """
    Get the current season based on the current date and time.

    Returns:
        str: The current season.

    """
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    return get_season(seven_days_ago)

def get_season(date: datetime)->int:
    """
    Returns the season based on the given date.

    Args:
        date (datetime.date): The date for which the season needs to be determined.

    Returns:
        int: The season number. 1 for winter, 2 for spring, 3 for summer, and 4 for autumn.

    """
    month = date.month
    if month in [12, 1, 2]:
        return 1
    elif month in [3, 4, 5]:
        return 2
    elif month in [6, 7, 8]:
        return 3
    elif month in [9, 10, 11]:
        return 4

def add_meteorological_season(df: pd.DataFrame, date_column: str)->pd.DataFrame:
    def get_season(date):
        month = date.month
        if month in [12, 1, 2]:
            return 1
        elif month in [3, 4, 5]:
            return 2
        elif month in [6, 7, 8]:
            return 3
        elif month in [9, 10, 11]:
            return 4
    
    # Ensure the date column is in datetime format
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Apply the get_season function to the date column and add it as a new column
    df['season'] = df[date_column].apply(get_season)
    
    return df

def get_var(varname: str) -> str:
    """
    Retrieves the value of a given environment variable or secret from the Streamlit configuration.

    If the current host is the local machine (according to the hostname), the environment variable is looked up in the system's environment variables.
    Otherwise, the secret value is fetched from Streamlit's secrets dictionary.

    Args:
        varname (str): The name of the environment variable or secret to retrieve.

    Returns:
        The value of the environment variable or secret, as a string.

    Raises:
        KeyError: If the environment variable or secret is not defined.
    """
    if socket.gethostname().lower() == LOCAL_HOST:
        return os.environ[varname]
    else:
        return st.secrets[varname]