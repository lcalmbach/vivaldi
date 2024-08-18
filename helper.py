import pandas as pd

season_name = {1:'Winter', 2:'Frühling', 3:'Sommer', 4:'Herbst'}

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

def add_meteorological_season(df, date_column):
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