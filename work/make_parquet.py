import pandas as pd

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

# Load the CSV file into a pandas DataFrame
csv_file_path = "./data/100254.csv"
df = pd.read_csv(csv_file_path, sep=';')
cols = ['Datum','Jahr','Tagesmittel Lufttemperatur','Tagesminimum Lufttemperatur', 'Tagesmaximum Lufttemperatur']
df = df[cols]
df.columns = ['date','year','temperature', 'min_temperature', 'max_temperature']
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(by='date')
df['season_year'] = df['date'].apply(lambda x: x.year + 1 if x.month == 12 else x.year)
df = add_meteorological_season(df, 'date')
df['day_in_season'] = df.groupby(['season', 'season_year']).cumcount() + 1

parquet_file_path = "./data/100254.parquet"
df.to_parquet(parquet_file_path)
df.to_csv("./data/100254_season.csv", index=False)
