import streamlit as st
import pandas as pd
import altair as alt
import const as cn

menu = ["Statisitik der Jahreszeiten", "Vergleich Jahreszeit-Temperatur Mittelwerte"]


def cumulative_average(df: pd.DataFrame, sort_key: str, value_key: str) -> pd.DataFrame:
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
    plot_data["main_year"] = plot_data["Jahr"] == settings["main_year"]
    if "y_axis" in settings:
        y_axis = alt.Y(f"{settings['y']}:Q", scale=alt.Scale(domain=settings["y_axis"]))
    else:
        y_axis = alt.Y(f"{settings['y']}:Q")
    line_chart = (
        alt.Chart(plot_data)
        .mark_line()
        .encode(
            x=f"{settings['x']}:Q",
            y=y_axis,
            color=f"{settings['color']}:N",
            size=alt.condition(alt.datum["main_year"], alt.value(3), alt.value(1)),
            tooltip=[settings["x"], settings["y"], settings["color"]],
        )
        .properties(title=settings["title"], height=400)
    )
    st.altair_chart(line_chart, use_container_width=True)


def plot_histogram(plot_data: pd.DataFrame, settings: dict):
    """
    Plots a histogram using the provided plot_data and settings.

    Parameters:
    - plot_data (pandas.DataFrame): The data to be plotted.
    - settings (dict): A dictionary containing the plot settings.

    Returns:
    None
    """
    histogram = (
        alt.Chart(plot_data)
        .mark_bar()
        .encode(
            alt.X(f"{settings['y']}:Q", bin=alt.Bin(maxbins=50)),  # Specify maxbins here
            alt.Y("count()", title="Anzahl"),
            alt.Color(f"{settings['color']}:N", legend=alt.Legend(title="Jahr")),
            alt.Facet(f"{settings['color']}:N", columns=1, title=settings["title"]),
        )
        .properties(width=400, height=300)
        .configure_facet(spacing=10)
        .configure_title(anchor="middle")
    )

    st.altair_chart(histogram, use_container_width=True)


def add_day_column(vivaldi, df) -> pd.DataFrame:
    """
    Adds a day column to the given DataFrame based on the specified time aggregation.

    Parameters:
        vivaldi (object): An object containing information about the time aggregation.
        df (pd.DataFrame): The DataFrame to which the day column will be added.

    Returns:
        pd.DataFrame: The DataFrame with the day column added.

    Raises:
        None
    """
    # ranks data by date and season
    if vivaldi.time_agg == "Jahreszeit":
        df[vivaldi.day_in_period_column] = (
            df.groupby(["season", "season_year"]).cumcount() + 1
        )
    elif vivaldi.time_agg == "Jahr":
        df[vivaldi.day_in_period_column] = df.groupby(["year"]).cumcount() + 1
    elif vivaldi.time_agg == "Monat":
        df[vivaldi.day_in_period_column] = df.groupby(["year", "month"]).cumcount() + 1
    return df


def get_main_year_data(vivaldi, df_all):
    """
    Filter the given DataFrame `df_all` to include only the main year data based on the `vivaldi` object.
    Perform necessary data transformations and return the resulting DataFrame.

    Parameters:
    - vivaldi: The Vivaldi object used for filtering and data transformations.
    - df_all: The DataFrame containing all the data.

    Returns:
    - df: The filtered and transformed DataFrame containing the main year data.
    """
    df = vivaldi.filter_by_main_year(df_all)
    df, add_day_column(vivaldi, df)
    df = df.drop(columns=["date"])
    if "season_year" in df.columns:
        year_col, year_expression = "season_year", "Jahr"
    else:
        year_col, year_expression = "year", "Jahr"
    col_to_drop = [x for x in df.columns if x in ["month", "season"]]
    df = df.drop(col_to_drop, axis=1)
    df.rename(
        columns={vivaldi.parameter: vivaldi.parameter_label, year_col: year_expression},
        inplace=True,
    )
    return df


def get_climat_normal_data(vivaldi, df_all):
    """
    Retrieves climate normal data from the given DataFrame.

    Args:
        vivaldi (Vivaldi): An instance of the Vivaldi class.
        df_all (pandas.DataFrame): The input DataFrame containing all data.

    Returns:
        pandas.DataFrame: The DataFrame with climate normal data, aggregated by day.

    """
    df = vivaldi.filter_by_climate_normal(df_all)
    df = add_day_column(vivaldi, df)
    df = (
        df.groupby(vivaldi.day_in_period_column)
        .agg(
            {vivaldi.parameter: "mean"}
        )
        .reset_index()
    )
    df.rename(columns={vivaldi.parameter: vivaldi.parameter_label}, inplace=True)
    return df


def get_compare_to_selected_years_data(vivaldi, df_all):
    """
    Retrieves data for comparing the main year with selected years.

    Args:
        vivaldi (Vivaldi): An instance of the Vivaldi class.
        df_all (DataFrame): The DataFrame containing the data.

    Returns:
        tuple: A tuple containing two DataFrames:
            - plot_data: The modified plot data for comparison.
            - plot_data_base: The base plot data.

    """
    plot_data_base = vivaldi.filter_by_multi_year(
        df_all, [vivaldi.main_year] + vivaldi.multi_years
    )
    plot_data_base = add_day_column(vivaldi, plot_data_base)

    if cn.parameters_dict[vivaldi.parameter]["agg_func"][0] == "sum":
        plot_data = plot_data_base.copy()
        sort_by_columns = vivaldi.time_aggregation_parameters + [
            vivaldi.day_in_period_column
        ]
        plot_data[vivaldi.parameter] = (
            plot_data.sort_values(by=sort_by_columns)
            .groupby(vivaldi.time_aggregation_parameters)[vivaldi.parameter]
            .cumsum()
        )
    else:
        plot_data = plot_data_base
    plot_data = vivaldi.rename_plot_columns(plot_data)
    plot_data["main_year"] = 0
    return plot_data, plot_data_base


def get_compare_climate_normal_data(vivaldi, df_all):
    df_main = get_main_year_data(vivaldi, df_all)
    df_climate_normal = get_climat_normal_data(vivaldi, df_all)
    plot_data_base = pd.concat([df_main.copy(), df_climate_normal.copy()], ignore_index=True)
    if cn.parameters_dict[vivaldi.parameter]["agg_func"][0] == "sum":
        df_main[vivaldi.parameter_label] = df_main[vivaldi.parameter_label].cumsum()
        df_climate_normal[vivaldi.parameter_label] = df_climate_normal[
            vivaldi.parameter_label
        ].cumsum()
    else:
        plot_data = pd.concat([df_main, df_climate_normal], ignore_index=True)

    plot_data = pd.concat([df_main, df_climate_normal], ignore_index=True)
    return plot_data, plot_data_base


def show(vivaldi):
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

    df_all = vivaldi.data[
        vivaldi.time_aggregation_parameters + ["date", vivaldi.parameter]
    ]
    if vivaldi.compare_type == 0:  # selected years
        plot_data, plot_data_base = get_compare_to_selected_years_data(vivaldi, df_all)
    else:  # climate normal
        plot_data, plot_data_base = get_compare_climate_normal_data(vivaldi, df_all)

    plot_data["main_year"] = plot_data["Jahr"] == vivaldi.main_year
    settings = {
        "title": f"{vivaldi.parameter_label} im {vivaldi.period_name}",
        "x": vivaldi.day_in_period_column,
        "y": vivaldi.parameter_label,
        "color": "Jahr",
        "main_year": vivaldi.main_year,
    }
    if not vivaldi.y_axis_auto:
        settings["y_axis"] = vivaldi.y_axis
    plot_line_chart(plot_data, vivaldi.main_year, settings)

    # cumulative average only makes sense for continuous data such as temperature, not for e.g. precipitation
    if cn.parameters_dict[vivaldi.parameter]["agg_func"][0] == "mean":
        # lower plots  shows cumulative average
        st.markdown("---")
        cumulative_comparison_data = pd.DataFrame()
        if vivaldi.compare_type == 0:
            cumulative_comparison_data = pd.DataFrame()
            for year in [vivaldi.main_year] + vivaldi.multi_years:
                df = cumulative_average(
                    plot_data[plot_data["Jahr"] == year],
                    vivaldi.day_in_period_column,
                    vivaldi.parameter_label,
                )
                df["Jahr"] = year
                cumulative_comparison_data = pd.concat([cumulative_comparison_data, df])
        else:
            df_main = get_main_year_data(vivaldi, df_all)
            df_main = cumulative_average(
                df_main, vivaldi.day_in_period_column, vivaldi.parameter_label
            )
            df_main["Jahr"] = vivaldi.main_year

            df_climate_normal = get_climat_normal_data(vivaldi, df_all)
            df_climate_normal = cumulative_average(
                df_climate_normal, vivaldi.day_in_period_column, vivaldi.parameter_label
            )
            df_climate_normal["Jahr"] = cn.climate_normal_name_dict[
                vivaldi.compare_type
            ]
            cumulative_comparison_data = pd.concat([df_main, df_climate_normal])

            cumulative_comparison_data["main_year"] = (
                cumulative_comparison_data["Jahr"] == vivaldi.main_year
            )
            plot_data = pd.concat(
                [df_main, cumulative_comparison_data], ignore_index=True
            )

        settings["title"] = (
            f"Kumulatives Mittel von {vivaldi.parameter_label} im {vivaldi.period_name}"
        )
        settings["Y_title"] = f"Anzahl"
        plot_line_chart(cumulative_comparison_data, vivaldi.main_year, settings)

    # Histogram
    st.markdown("---")
    if cn.parameters_dict[vivaldi.parameter]["agg_func"][0] == "sum":
        plot_data = plot_data_base
        plot_data = vivaldi.rename_plot_columns(plot_data)
    settings["title"] = (
        f"Histogramm von {vivaldi.parameter_label} im {vivaldi.period_name}",
    )
    plot_histogram(plot_data, settings)
