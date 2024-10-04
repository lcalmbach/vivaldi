import streamlit as st
import pandas as pd
from datetime import datetime
import const as cn

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
    if row["Jahr"] == current_year:
        return ["background-color: yellow"] * len(row)
    return [""] * len(row)


def show(vivaldi):
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
    df = vivaldi.data
    ranked_parameter_column = vivaldi.get_col_name(vivaldi.ranked_parameter)
    if vivaldi.time_agg == "Jahreszeit":
        # filter is applied to ogitinal table with original names, not labels
        filtered_df = df[
            (df["season"].isin(vivaldi.filter_seasons))
            & (df["season_year"] >= vivaldi.filter_years[0])
            & (df["season_year"] <= vivaldi.filter_years[1])
            & (df[ranked_parameter_column].notna())
        ]
        year_field = "season_year"
        agg_field = "season"
        agg_field_de = "Jahreszeit"
        map_func = cn.season_name
    elif vivaldi.time_agg == "Monat":
        filtered_df = df[
            (df["month"].isin(vivaldi.filter_months))
            & (df["season_year"] >= vivaldi.filter_years[0])
            & (df["season_year"] <= vivaldi.filter_years[1])
            & (df[ranked_parameter_column].notna())
        ]
        year_field = "year"
        agg_field = "month"
        agg_field_de = "Monat"
        map_func = vivaldi.month_name
    else:
        filtered_df = df
        year_field = "year"
        agg_field = "year"
        agg_field_de = "Jahr"
    # Generate the summary table grouped by year and season
    summary_table = (
        filtered_df.groupby(vivaldi.time_aggregation_parameters)
        .agg(
            {
                ranked_parameter_column: cn.parameters_dict[ranked_parameter_column][
                    "agg_func"
                ]
            }
        )
        .reset_index()
    )
    # Rename columns for better readability
    if vivaldi.time_agg != "Jahr":
        summary_table[agg_field] = summary_table[agg_field].map(map_func)
    parameter_agg_list = [
        f"{vivaldi.ranked_parameter} ({cn.agg_func_dict[f]})"
        for f in cn.parameters_dict[ranked_parameter_column]["agg_func"]
    ]
    if vivaldi.time_agg != "Jahr":
        summary_table.columns = ["Jahr", agg_field_de] + parameter_agg_list
    else:
        summary_table.columns = ["Jahr"] + parameter_agg_list
    summary_table["Rang"] = summary_table[parameter_agg_list[0]].rank(
        ascending=False, method="min"
    )
    summary_table["Rang"] = summary_table["Rang"].astype(int)
    summary_table.sort_values(by="Jahr", inplace=True, ascending=False)

    formats = {
        f"{vivaldi.ranked_parameter} ({cn.agg_func_dict[f]})": cn.parameters_dict[
            ranked_parameter_column
        ]["frmt"]
        for f in cn.parameters_dict[ranked_parameter_column]["agg_func"]
    }
    styled_table = summary_table.style.apply(highlight_current_year_row, axis=1).format(
        formats
    )

    st.title(f"Statistik der Temperaturen nach {agg_field_de}, Station Binningen")
    st.subheader(f"Jahre {vivaldi.filter_years[0]} - {vivaldi.filter_years[1]}")
    st.dataframe(
        styled_table,
        height=800,
        width=1000,
        hide_index=True,
    )

    st.title("Einzeldaten")
    st.subheader(f"Jahre {vivaldi.filter_years[0]} - {vivaldi.filter_years[1]}")
    df = vivaldi.data.sort_values(by="date", ascending=False)
    if vivaldi.time_agg == "Jahreszeit":
        filtered_df = df[
            (df["season"].isin(vivaldi.filter_seasons))
            & (df["year"] >= vivaldi.filter_years[0])
            & (df["year"] <= vivaldi.filter_years[1])
        ]
    elif vivaldi.time_agg == "Monat":
        filtered_df = df[
            (df["month"].isin(vivaldi.filter_months))
            & (df["year"] >= vivaldi.filter_years[0])
            & (df["year"] <= vivaldi.filter_years[1])
        ]
    elif vivaldi.time_agg == "Jahr":
        filtered_df = df[
            (df["year"] >= vivaldi.filter_years[0])
            & (df["year"] <= vivaldi.filter_years[1])
        ]
    filtered_df = filtered_df[["date"] + list(cn.parameters_dict.keys())]
    filtered_df.columns = ["Datum"] + list(
        v["label"] for v in cn.parameters_dict.values()
    )
    formats = {"Datum": lambda x: x.strftime("%d.%m.%Y")}
    for k, v in cn.parameters_dict.items():
        formats[v["label"]] = v["frmt"]
    styled_df = filtered_df.style.format(formats)
    st.dataframe(styled_df, height=800, width=1000, hide_index=True)
