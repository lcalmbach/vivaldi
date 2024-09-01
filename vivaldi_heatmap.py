import streamlit as st
import pandas as pd
from datetime import datetime
import helper
import altair as alt

season_mapping = {
        1: 'Winter',
        2: 'Frühling',
        3: 'Sommer',
        4: 'Herbst'
    }
ranking_options = ['temperature', 'min_temperature', 'max_temperature']
function_dict = {
    'temperature': 'mean',
    'min_temperature': 'min',
    'max_temperature': 'max',
    'hitzetag': 'sum',
    'frosttag': 'sum',
    'eistag': 'sum'
}


def create_heatmap(df, par_title):
    par = df.columns[-1]
    heatmap = alt.Chart(df).mark_rect().encode(
    x=alt.X('Jahreszeit:N', title='Jahreszeit', sort=['Winter', 'Frühling', 'Sommer', 'Herbst']),
    y=alt.Y('Jahr:O', title='Jahr', sort=alt.SortField('year', order='descending')),  # Most recent year on top
    color=alt.Color(f'{par}:Q', title='Temperature (°C)', scale=alt.Scale(
        range=['lightblue', 'red']  # Light blue to red gradient
    )),
    tooltip=['Jahr', 'Jahreszeit', par]
    ).properties(
        width=400,
        height=1200,
        title=f'Jahreszeiten Heatmap ({par_title})'
    )
    return heatmap
    

def show():
    df = st.session_state.data
    season_mapping = {1: 'Winter', 2: 'Frühling', 3: 'Sommer', 4: 'Herbst'}
    parameter_dict = {
        'temperature': 'Mittl. Temp[°C]',
        'min_temperature': 'Min Temp[°C]', 
        'max_temperature': 'Max Temp[°C]',
    }
    
    # Add a season filter to the sidebar
    min_year, max_year = int(df['year'].min()), int(df['year'].max())
    selected_year_range = st.sidebar.slider(
        "Select Year Range", min_year, max_year, (min_year, max_year)
    )

    filtered_df = df[
        (df['season_year'] >= selected_year_range[0]) &
        (df['season_year'] <= selected_year_range[1])
    ]
    parameter = st.sidebar.selectbox("Parameter", ranking_options)
    # Generate the summary table grouped by year and season
    summary_table = filtered_df.groupby(['season_year', 'season']).agg(
        {parameter: function_dict[parameter]}
    ).reset_index()
    summary_table = summary_table.sort_values(by='season_year', ascending=False)
    summary_table.columns = ['Jahr', 'Jahreszeit', parameter]
    
    summary_table['Jahreszeit'] = summary_table['Jahreszeit'].replace(season_mapping)
    heatmap = create_heatmap(summary_table, parameter_dict[parameter])
    st.altair_chart(heatmap, use_container_width=True)

    csv = summary_table.to_csv(index=False)
    st.download_button(
        label="Daten Herunterladen",
        data=csv,
        file_name='seasonal_temperature_summary.csv',
        mime='text/csv'
    )
