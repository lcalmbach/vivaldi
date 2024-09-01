import streamlit as st
import pandas as pd
from datetime import datetime
import helper

current_year = datetime.now().year
pd.set_option("styler.render.max_elements", 660000)



def highlight_current_year_row(row):
    """
    Highlights the current year row in a DataFrame.

    Parameters:
    - row: A pandas Series representing a row in a DataFrame.

    Returns:
    - A list of CSS styles to apply to each cell in the row. If the row represents the current year, the style will be 'background-color: yellow', otherwise an empty string.

    Example:
    >>> df = pd.DataFrame({'Jahr': [2020, 2021, 2022]})
    >>> df.apply(highlight_current_year_row, axis=1)
    """
    if row['Jahr'] == current_year:
        return ['background-color: yellow'] * len(row)
    return [''] * len(row)

def show():
    """
    Displays statistics and individual data for seasonal temperatures.

    This function generates a summary table and individual data table for seasonal temperatures.
    It allows the user to select the seasons, year range, and ranking parameter for the summary table.
    The summary table is displayed with highlighted rows for the current year.
    The individual data table is displayed with columns for date, year, temperature, min_temperature,
    max_temperature, and day_in_season.

    Parameters:
        None

    Returns:
        None
    """
    df = st.session_state.data
    season_mapping = {1: 'Winter', 2: 'Frühling', 3: 'Sommer', 4: 'Herbst'}
    ranking_options = ['Mittl. Temp', 'Min Temp', 'Max Temp', 'Hitzetage', 'Eistage', 'Frosttage']

    # Add a season filter to the sidebar
    selected_seasons = st.sidebar.multiselect( 
        "Selektiere Jahreszeit", options=list(season_mapping.keys()),
        format_func=lambda x: season_mapping[x],
        default=helper.get_current_season()
    )
    if selected_seasons == []:
        selected_seasons = df['season'].unique()
    min_year, max_year = int(df['year'].min()), int(df['year'].max())
    selected_year_range = st.sidebar.slider(
        "Select Year Range", min_year, max_year, (min_year, max_year)
    )

    filtered_df = df[
        (df['season'].isin(selected_seasons)) &
        (df['season_year'] >= selected_year_range[0]) &
        (df['season_year'] <= selected_year_range[1])
    ]

    # Generate the summary table grouped by year and season
    summary_table = filtered_df.groupby(['season_year', 'season']).agg({
        'temperature': ['mean'],
        'min_temperature': ['min'],
        'max_temperature': ['max'],
        'hitzetag': ['sum'],
        'frosttag': ['sum'],
        'eistag': ['sum']
    }).reset_index()

    ranked_parameter = st.sidebar.selectbox("Ranking Parameter", ranking_options)
    # Rename columns for better readability
    summary_table['season'] = summary_table['season'].map(season_mapping)
    summary_table.columns = ['Jahr', 'Jahreszeit', 'Mittl. Temp', 'Min. Temp', 'Max. Temp', 'Hitzetage', 'Frosttage', 'Eistage']
    summary_table['Rang'] = summary_table[ranked_parameter].rank(ascending=False, method='min')
    summary_table['Rang'] = summary_table['Rang'].astype(int)
    summary_table.sort_values(by='Jahr', inplace=True, ascending=False)
    styled_table = summary_table.style.apply(highlight_current_year_row, axis=1).format({
        "Mittl. Temp": "{:.1f}",
        "Min. Temp": "{:.1f}",
        "Max. Temp": "{:.1f}"
    })

    st.title("Statistik der Temperaturen nach Jahreszeiten, Station Binningen")
    st.subheader(f"Jahre {selected_year_range[0]} - {selected_year_range[1]}")
    st.dataframe(
        styled_table, 
        height=800, 
        width=1000, 
        hide_index=True,
    )
    

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
    filtered_df = filtered_df[['date', 'temperature', 'min_temperature', 'max_temperature', 'day_in_season']]
    filtered_df.columns = ['Datum', 'Mittl. Temp', 'Min. Temp', 'Max. Temp', 'Tag in Jahreszeit']
    styled_df = filtered_df.style.format({
        'Datum': lambda x: x.strftime('%d.%m.%Y'),
        "Mittl. Temp": "{:.1f}",
        "Min. Temp": "{:.1f}",
        "Max. Temp": "{:.1f}"
    })
    st.dataframe(styled_df, height=800, width=1000, hide_index=True)
