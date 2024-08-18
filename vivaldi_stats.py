import streamlit as st
import pandas as pd
from datetime import datetime

current_year = datetime.now().year
pd.set_option("styler.render.max_elements", 469312)



def highlight_current_year_row(row):
    if row['Jahr'] == current_year:
        return ['background-color: yellow'] * len(row)
    return [''] * len(row)

def show():
    df = st.session_state.data
    season_mapping = {1: 'Winter', 2: 'Frühling', 3: 'Sommer', 4: 'Herbst'}
    ranking_options = ['Mittl. Temp', 'Min Temp', 'Max Temp']

    # Add a season filter to the sidebar
    selected_seasons = st.sidebar.multiselect( 
        "Selektiere Jahreszeit", options=list(season_mapping.keys()),
        format_func=lambda x: season_mapping[x]
    )
    if selected_seasons == []:
        selected_seasons = df['season'].unique()
    min_year, max_year = int(df['year'].min()), int(df['year'].max())
    selected_year_range = st.sidebar.slider(
        "Select Year Range", min_year, max_year, (min_year, max_year)
    )

    filtered_df = df[
        (df['season'].isin(selected_seasons)) &
        (df['year'] >= selected_year_range[0]) &
        (df['year'] <= selected_year_range[1])
    ]

    # Generate the summary table grouped by year and season
    summary_table = filtered_df.groupby(['year', 'season']).agg({
        'temperature': ['mean'],
        'min_temperature': ['min'],
        'max_temperature': ['max']
    }).reset_index()

    ranked_parameter = st.sidebar.selectbox("Ranking Parameter", ranking_options)
    # Rename columns for better readability
    summary_table['season'] = summary_table['season'].map(season_mapping)
    summary_table.columns = ['Jahr', 'Jahreszeit', 'Mittl. Temp', 'Min Temp', 'Max Temp']
    summary_table['Rang'] = summary_table[ranked_parameter].rank(ascending=False, method='min')


    # Apply the style to the 'year' column
    styled_df = summary_table.style.apply(highlight_current_year_row, axis=1)

    st.title("Statistik der Temperaturen nach Jahreszeiten, Station Binningen")
    st.subheader(f"Jahre {selected_year_range[0]} - {selected_year_range[1]}")
    st.dataframe(styled_df, height=800, width=1000, hide_index=True)

    csv = summary_table.to_csv(index=False)
    st.download_button(
        label="Daten Herunterladen",
        data=csv,
        file_name='seasonal_temperature_summary.csv',
        mime='text/csv'
    )

    st.title("Einzeldaten")
    st.subheader(f"Jahre {selected_year_range[0]} - {selected_year_range[1]}")
    df = st.session_state.data.sort_values(by='date', ascending=False)
    filtered_df = df[
        (df['season'].isin(selected_seasons)) &
        (df['year'] >= selected_year_range[0]) &
        (df['year'] <= selected_year_range[1])
    ]
    filtered_df = filtered_df[['date', 'year', 'temperature', 'min_temperature', 'max_temperature', 'day_in_season']]
    st.dataframe(filtered_df, height=800, width=1000, hide_index=True)
