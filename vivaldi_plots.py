import streamlit as st
import pandas as pd
import altair as alt
import helper


season_dict = {1: [12,1,2], 2: [3,4,5], 3: [6,7,8], 4: [9,10,11]} 
seasons_id = {"Winter":1, "Frühling":2, "Sommer":3, "Herbst": 4}
menu = ['Statisitik der Jahreszeiten', 'Vergleich Jahreszeit-Temperatur Mittelwerte']
DEF_NORM_START, DEF_NORM_END = 1991, 2020        

def cumulative_average(df: pd.DataFrame, sort_key:str, value_key:str)->pd.DataFrame:
    """
    Calculate the cumulative average of a specified column in a DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        sort_key (str): The column name used for sorting the DataFrame.
        value_key (str): The column name for which the cumulative average is calculated.

    Returns:
        pandas.DataFrame: A DataFrame containing the sorted values of `sort_key` and the cumulative average of `value_key`.
    """
    df_year = df.sort_values(by=sort_key)
    df_year[value_key] = df_year[value_key].expanding().mean()
    result = df_year[[sort_key, value_key]]
    return result


def get_main_data(all_data:pd.DataFrame, main_year:int, season:int)->pd.DataFrame:
    """
    Retrieves the main data for a specific year and season from the given dataset.

    Parameters:
    - all_data (DataFrame): The dataset containing all the data.
    - main_year (int): The main year to filter the data by.
    - season (str): The season to filter the data by.

    Returns:
    - main_year_data (DataFrame): The filtered data for the main year and season.
    """
    main_year_data = all_data[(all_data['season_year'] == main_year) & (all_data['season'] == season)]
    main_year_data['year'] = f'{helper.season_name[season]} {main_year}'
    return main_year_data


def get_comparison_data(all_data:pd.DataFrame, compare_type:str, comparison_years:list, climate_normal:list, season:int):
    """
    Retrieves comparison data based on the specified parameters.

    Parameters:
    - all_data: DataFrame containing all the data
    - compare_type: Type of comparison ('Jahr' or other)
    - comparison_years: List of years to compare
    - climate_normal: Range of years for climate normal
    - season: Season to consider

    Returns:
    - comparison_data: DataFrame containing the comparison data
    """

    if compare_type == 'Jahr':
        comparison_data = all_data[(all_data['season'] == season) & (all_data['season_year'].isin(comparison_years)) ]
        comparison_data = comparison_data[['season_year', 'day_in_season', 'temperature']]
        comparison_data['year'] = comparison_data['season_year'].astype(str)
        comparison_data['year'] = helper.season_name[season] + ' ' + comparison_data['year']
    else:
        normal_data = all_data[(all_data['season_year'] >= climate_normal[0]) & (all_data['season_year'] <= climate_normal[1]) & ( all_data['season'] == season)]
        normal_data = normal_data.groupby('day_in_season').agg({'temperature':'mean'}).reset_index()
        normal_data['year'] = f'{helper.season_name[season]} {climate_normal[1]} - {climate_normal[0]}'
        comparison_data = normal_data
    
    return comparison_data.sort_values(by='day_in_season')


def plot_line_chart(plot_data, main_year: int, settings: dict):
    """
    Plots a line chart using the provided data.

    Parameters:
    - plot_data (pandas.DataFrame): The data to be plotted.
    - main_year (int): The main year to highlight in the chart.
    - settings (dict): Additional settings for the chart.

    Returns:
    None
    """
    plot_data['is_main_year'] = plot_data['year'].str.contains(str(main_year))
    line_chart = alt.Chart(plot_data).mark_line().encode(
        x='day_in_season:Q',
        y='temperature:Q',
        color='year:N',
        size=alt.condition(
            alt.datum['is_main_year'],
            alt.value(3),
            alt.value(1)
        ),
        tooltip=['year', 'day_in_season', 'temperature']
    ).properties(
        title=settings['title']
    )
    st.altair_chart(line_chart, use_container_width=True)


def plot_histogram(plot_data:pd.DataFrame, settings:dict):
    """
    Plots a histogram using the provided plot_data and settings.

    Parameters:
    - plot_data (pandas.DataFrame): The data to be plotted.
    - settings (dict): A dictionary containing the plot settings.

    Returns:
    None
    """
    histogram = alt.Chart(plot_data).mark_bar().encode(
        alt.X('temperature:Q', bin=True, title='Temperatur [°C]'),
        alt.Y('count()', title='Count'),
        alt.Color('season_year:N', legend=alt.Legend(title="Jahr")),
        alt.Facet('season_year:N', columns=1, title=settings['title'])
    ).properties(
        width=400,
        height=300
    ).configure_facet(
        spacing=10
    ).configure_title(
        anchor='middle'
    )

    st.altair_chart(histogram, use_container_width=True)


def get_filters():
    """
    Returns the selected filters for generating Vivaldi plots.

    Returns:
        tuple: A tuple containing the following elements:
            - season (str): The selected season.
            - main_year (int): The selected main year.
            - compare_type (str): The type of comparison selected.
            - comparison_years (list): The selected comparison years.
            - climate_normal (list): The selected climate normal range.
    """
    st.sidebar.header("Select Filters")
    
    index = helper.get_current_season() -1
    season = seasons_id[st.sidebar.selectbox("Wähle eine Jahreszeit", seasons_id.keys(), index=index)]
    main_year = st.sidebar.selectbox("Wähle das Hauptjahr", st.session_state.years )
    
    compare_options=["Jahr", "Klimanormale"]
    compare_type = st.sidebar.radio("Vergleiche ausgewählte Jahreszeit mit", compare_options)
    comparison_years, climate_normal, normal_start, normal_end = [st.session_state.years[1],st.session_state.years[2],st.session_state.years[3]], [], DEF_NORM_START, DEF_NORM_END
    if compare_options.index(compare_type) == 0:
        comparison_years = st.sidebar.multiselect("Vergleichsjahre", st.session_state.years, default=comparison_years)
    else:
        climate_normal = st.sidebar.select_slider("Klimanormale", sorted(st.session_state.years), value=[normal_start,normal_end])
    return season, main_year, compare_type, comparison_years, climate_normal


def show():
    """
    Displays graphical representations of temperature data.

    This function retrieves filters, main year data, and comparison data based on the selected season, main year,
    comparison type, comparison years, and climate normal. It then plots line charts and histograms to visualize the
    temperature data.

    Parameters:
        None

    Returns:
        None
    """
    st.title("Grafische Darstellungen")

    season, main_year, compare_type, comparison_years, climate_normal = get_filters()
    main_year_data = get_main_data(st.session_state.data , main_year, season)
    comparison_data = get_comparison_data(st.session_state.data, compare_type, comparison_years, climate_normal, season)
    plot_data = pd.concat([main_year_data, comparison_data])
    settings = {'title': f'Verlauf der mittleren Tagestemperatur im {helper.season_name[season]}'}
    plot_line_chart(plot_data, main_year, settings)
    st.write('---')

    cumulative_main_year_data = cumulative_average(main_year_data, 'day_in_season', 'temperature')
    cumulative_main_year_data['year'] = str(main_year)
    if compare_type == 'Jahr':
        cumulative_comparison_data = pd.DataFrame()
        for year in comparison_years:
            df = cumulative_average(comparison_data[comparison_data['season_year'] == year], 'day_in_season', 'temperature')
            df['year'] = str(year)
            cumulative_comparison_data = pd.concat([cumulative_comparison_data, df])
    else:
        cumulative_comparison_data = cumulative_average(comparison_data, 'day_in_season', 'temperature')
        cumulative_comparison_data['year'] = f'{climate_normal[1]} - {climate_normal[0]}'

    plot_data = pd.concat([cumulative_main_year_data, cumulative_comparison_data])
    settings = {'title': f'Verlauf des kumulativen Tagestemperatur-Mittelwerts im {helper.season_name[season]}'}
    plot_line_chart(plot_data, main_year, settings)
    st.write('---')

    settings = {'title': f'Histogramm der Tagestemperaturen'}
    plot_data = pd.concat([main_year_data, comparison_data]) if compare_type =='Jahr' else main_year_data
    plot_histogram(plot_data, settings)


    