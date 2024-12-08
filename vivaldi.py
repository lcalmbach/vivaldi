from typing import Tuple
import numpy as np
import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import const as cn
import os

import vivaldi_stats, vivaldi_chat, vivaldi_plots
from texts import txt

source_url = "https://data.bs.ch/api/records/1.0/search/?dataset=100254&q=date%20%3E%20%22{}%22&rows=100&sort=date"
url_all_data = "https://data.bs.ch/api/explore/v2.1/catalog/datasets/100254/exports/csv?lang=de&timezone=Europe%2FBerlin&use_labels=false&delimiter=%3B"
parquet_file_path = "data/100254.parquet"


LOCAL_HOST = "gladiator"
compare_options = {
    0: "Jahre",
    1: "Klimanormale 1991-2020",
    2: "Klimanormale 1961-2090",
    3: "Klimanormale 1864-1960",
}


class Vivaldi:
    def __init__(self):
        self.data = self.get_data()
        self.data.reset_index
        self.parameter = list(cn.parameters_dict.keys())[0]
        self.ranked_parameter = list(cn.parameters_dict.keys())[0]
        self.time_agg = cn.time_agg_options[1]
        # season, month or year to which we want to compare the historic data
        self.main_season = self.get_default_season()
        self.main_month = self.get_default_month()
        self.main_year = self.data["year"].max()

        # limit compare data in stats to
        self.filter_seasons = [self.get_default_season()]
        self.filter_months = self.get_default_month()
        self.filter_years = [self.data["year"].min(), self.data["year"].max()]
        self.compare_type = 0
        self.multi_years = list(
            range(self.data["year"].max() - 3, self.data["year"].max())
        )
        self.climate_normal = [cn.DEF_NORM_START, cn.DEF_NORM_END]
        self.years = sorted(
            list(range(self.data["year"].min(), self.data["year"].max() + 1)),
            reverse=True,
        )
        self.y_axis_auto = True
        self.y_axis = [0.0, 0.0]
        self.type = "info"

    def get_default_month(self) -> int:
        """
        Get the last fully completed month and year

        Returns:
            int: The current month.

        """
        month = datetime.now().month
        if month == 1:
            return (12,)
        else:
            return month - 1

    def get_col_name(self, parameter: str) -> str:
        """
        Get the column name for the given parameter.

        Args:
            parameter (str): The parameter for which the column name is needed.

        Returns:
            str: The column name for the given parameter.

        """
        return cn.column_names_dict[parameter]

    def get_default_season(self):
        """
        Get the current cn.SeasonEnum based on the current date and time.

        Returns:
            str: The current cn.SeasonEnum.

        """
        today = datetime.now()
        season = self.get_season(today)
        if season > cn.SeasonEnum.WINTER.value:
            return season - 1
        else:
            return cn.SeasonEnum.AUTUMN.value


    def get_season(self, date: datetime) -> int:
        """
        Returns the cn.SeasonEnum based on the given date.

        Args:
            date (datetime.date): The date for which the cn.SeasonEnum needs to be determined.

        Returns:
            int: The cn.SeasonEnum number. 1 for winter, 2 for spring, 3 for summer, and 4 for autumn.

        """
        month = date.month
        if month in [12, 1, 2]:
            return cn.SeasonEnum.WINTER.value
        elif month in [3, 4, 5]:
            return cn.SeasonEnum.SPRING.value
        elif month in [6, 7, 8]:
            return cn.SeasonEnum.SUMMER.value
        elif month in [9, 10, 11]:
            return cn.SeasonEnum.AUTUMN.value

    def get_var(self, varname: str) -> str:
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
        return st.secrets[varname]

    def rename_plot_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Renames the columns of the DataFrame for plotting.

        Args:
            df (pandas.DataFrame): The DataFrame to be renamed.

        Returns:
            pandas.DataFrame: The DataFrame with renamed columns.

        """
        if self.time_agg == "Jahreszeit":
            df = df.rename(
                columns={
                    "season_year": "Jahr",
                }
            )
        elif self.time_agg == "Monat":

            df = df.rename(
                columns={
                    "year": "Jahr",
                    "month": "Monat",
                }
            )
        else:
            df = df.rename(
                columns={
                    "year": "Jahr",
                }
            )

        df = df.rename(
            columns={
                self.parameter: cn.parameters_dict[self.parameter]["label"],
            }
        )
        return df

    def create_parquet_file(self):
        """
        Creates a parquet file with the data from the API.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        df = pd.read_csv(url_all_data, sep=";")
        formatted_df = self.format_raw_data(df)
        formatted_df.to_parquet(parquet_file_path)
        return formatted_df
        
    def format_raw_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        def add_meteorological_season(
            df: pd.DataFrame, date_column: str
        ) -> pd.DataFrame:
            # Ensure the date column is in datetime format
            df[date_column] = pd.to_datetime(df[date_column])

            # Apply the get_season function to the date column and add it as a new column
            df["season"] = df[date_column].apply(self.get_season)

            return df
        
        base_fields = [
            "date",
            "jahr",
            "tre200d0",
            "tre200dn",
            "tre200dx",
            "rre150d0",
            "hto000d0",
            "gre000d0",
        ]

        fields = [
            f"fields.{field}" if "tre200d0" not in raw_df.columns else field
            for field in base_fields
        ]
        formatted_df = raw_df[fields]
        formatted_df.columns = [
            "date",
            "year",
            "temperature",
            "min_temperature",
            "max_temperature",
            "niederschlag",
            "schneemenge",
            "globalstrahlung"
        ]
        formatted_df["date"] = pd.to_datetime(formatted_df["date"])
        formatted_df = formatted_df.astype(
            {
                "year": "int32",
                "temperature": "float64",
                "min_temperature": "float64",
                "max_temperature": "float64",
                "niederschlag": "float64",
                "schneemenge": "float64",
                "globalstrahlung": "float64",
            }
        )
        formatted_df = formatted_df.sort_values(by="date")

        formatted_df["season_year"] = formatted_df["date"].apply(
            lambda x: x.year + 1 if x.month == 12 else x.year
        )
        formatted_df = add_meteorological_season(formatted_df, "date")
        formatted_df["day_in_season"] = (
            formatted_df.groupby(["season", "season_year"]).cumcount() + 1
        )
        formatted_df["hitzetag"] = np.where(formatted_df["max_temperature"] > 30, 1, 0)
        formatted_df["frosttag"] = np.where(formatted_df["min_temperature"] < 0, 1, 0)
        formatted_df["eistag"] = np.where(formatted_df["max_temperature"] < 0, 1, 0)
        return formatted_df.sort_values(by="date")

    def get_data(self):
        """
        Retrieves data from a parquet file and updates it with new records from an API.
        The function verifies if the last date in the DataFrame is more than 1 day before the current date. If so, it
        fetches new data from the API and appends it to the DataFrame.

        Args:
            parquet_file_path (str): The file path of the parquet file.

        Returns:ivaldi_info
            pandas.DataFrame: The updated DataFrame containing the data from the parquet file.

        Raises:
            None
        """

        
        # if parquet file exists, read it
        
        if not os.path.exists(parquet_file_path):
            parquet_df = self.create_parquet_file()
        else:
            parquet_df = pd.read_parquet(parquet_file_path)
            last_date = parquet_df["date"].max().date()
            two_days_ago = datetime.now().date() - timedelta(days=2)

            # Check if last_date is more than 2 days before the current date
            if last_date < two_days_ago:
                last_date_str = last_date.strftime("%Y-%m-%d")

                response = requests.get(source_url.format(last_date_str))

                # Check if the request was successful
                if response.status_code == 200:
                    # Extract the JSON data from the response
                    data = response.json()
                    new_records_df = pd.json_normalize(data["records"])
                    if len(new_records_df) > 0:
                        new_records_df = self.format_raw_data(new_records_df)
                        parquet_df = pd.concat([parquet_df, new_records_df])
                        parquet_df.reset_index(drop=True, inplace=True)
                        
            parquet_df.to_parquet(parquet_file_path)
        return parquet_df

    def get_settings(self, keys: list, multi_select: bool = False):

        with st.sidebar.expander("⚙️ Settings", expanded=True):
            if "parameter" in keys:
                par_dict = {k: v["label"] for k, v in cn.parameters_dict.items()}
                self.parameter = st.selectbox(
                    "Parameter",
                    options=list(par_dict.keys()),
                    format_func=lambda x: par_dict[x],
                )

            self.time_agg = st.selectbox(
                "Zeitliche Aggregation",
                options=cn.time_agg_options,
                index=cn.time_agg_options.index(self.time_agg),
            )
            if self.time_agg == "Jahreszeit":
                if multi_select:
                    self.filter_seasons = st.multiselect(
                        "Wähle Jahreszeiten",
                        options=list(cn.season_name.keys()),
                        format_func=lambda x: cn.season_name[x],
                        default=self.filter_seasons,
                    )
                else:
                    self.main_season = st.selectbox(
                        "Wähle Jahreszeiten",
                        options=list(cn.season_name.keys()),
                        format_func=lambda x: cn.season_name[x],
                        index=list(cn.season_name.keys()).index(self.main_season),
                    )
            elif self.time_agg == "Monat":
                if multi_select:
                    self.filter_months = st.multiselect(
                        "Wähle Monate",
                        options=list(cn.month_name.keys()),
                        format_func=lambda x: cn.month_name[x],
                        default=self.filter_months,
                    )
                else:
                    self.main_month = st.selectbox(
                        "Wähle Monat",
                        options=list(cn.month_name.keys()),
                        format_func=lambda x: cn.month_name[x],
                        index=list(cn.month_name.keys()).index(self.main_month),
                    )
            # year needs to be shown for all options
            if "year" in keys:
                self.main_year = st.selectbox(
                    "Wähle Jahr",
                    options=self.years,
                    index=self.years.index(self.main_year),
                )
            if "years" in keys:
                self.filter_years = st.slider(
                    "Jahre im Vergleich",
                    min_value=self.years[0],
                    max_value=self.years[-1],
                    value=self.filter_years,
                )

            if "compare_type" in keys:
                self.compare_type = st.selectbox(
                    "Vergleiche ausgewählte Jahreszeit mit",
                    options=list(compare_options.keys()),
                    format_func=lambda x: compare_options[x],
                )
                if self.compare_type == 0:
                    self.multi_years = st.multiselect(
                        "Wähle Jahre",
                        options=self.years,
                        default=self.multi_years,
                    )

            if "ranking_parameter" in keys:
                ranking_options = list(
                    {v["label"] for k, v in cn.parameters_dict.items()}
                )
                self.ranked_parameter = st.selectbox(
                    "Ranking Parameter", options=ranking_options
                )
            if "y_axis" in keys:
                self.y_axis_auto = st.checkbox(
                    "Y-Achse automatisch skalieren", self.y_axis_auto
                )
                if not self.y_axis_auto:
                    self.y_axis[0] = st.number_input(
                        "Start",
                        min_value=-100.0,
                        max_value=100.0,
                        step=1.0,
                        value=self.y_axis[0],
                    )
                    self.y_axis[1] = st.number_input(
                        "Ende",
                        min_value=-100.0,
                        max_value=100.0,
                        step=1.0,
                        value=self.y_axis[1],
                    )

    def show_plots(self):
        self.type = "plots"
        self.get_settings(
            keys=["time_agg", "compare_type", "parameter", "year", "y_axis"],
            multi_select=False,
        )
        vivaldi_plots.show(self)

    def show_stats(self):
        self.type = "stats"
        self.get_settings(
            keys=["time_agg", "ranking_parameter", "years"], multi_select=True
        )
        vivaldi_stats.show(self)

    def show_chat(self):
        self.type = "stats"
        self.get_settings(keys=["time_agg", "year", "years"], multi_select=False)
        vivaldi_chat.show(self)

    def filter_by_climate_normal(self, df: pd.DataFrame) -> pd.DataFrame:
        cnorm = cn.climate_normal_dict[self.compare_type]

        if self.time_agg == "Jahreszeit":
            return df[
                (df["season"] == self.main_season)
                & (df["season_year"] >= cnorm[0])
                & (df["season_year"] <= cnorm[1])
            ]
        elif self.time_agg == "Monat":
            return df[
                (df["month"] == self.main_month)
                & (df["year"] >= cnorm[0])
                & (df["year"] <= cnorm[1])
            ]
        else:
            return df[(df["year"] >= cnorm[0]) & (df["year"] <= cnorm[1])]

    def filter_by_multi_year(self, df: pd.DataFrame, years) -> pd.DataFrame:
        if self.time_agg == "Jahreszeit":
            return df[
                (df["season"] == self.main_season) & (df["season_year"].isin(years))
            ]
        elif self.time_agg == "Monat":
            return df[(df["month"] == self.main_month) & (df["year"].isin(years))]
        else:
            return df[(df["year"].isin(years))]

    def filter_by_main_year(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.time_agg == "Jahreszeit":
            return df[
                (df["season"] == self.main_season)
                & (df["season_year"] == self.main_year)
            ]
        elif self.time_agg == "Monat":
            return df[(df["month"] == self.main_month) & (df["year"] == self.main_year)]
        else:
            return df[(df["year"] == self.main_year)]

    def filter_by_period(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.time_agg == "Jahreszeit":
            return df[
                (df["season"] == self.main_season)
                & (df["season_year"] >= self.filter_years[0])
                & (df["season_year"] <= self.filter_years[1])
            ]
        elif self.time_agg == "Monat":
            return df[
                (df["month"] == self.main_month)
                & (df["year"] >= self.filter_years[0])
                & (df["year"] <= self.filter_years[1])
            ]
        else:
            return df

    @property
    def day_in_period_column(self):
        x = {
            "Jahreszeit": "Tag in Jahreszeit",
            "Monat": "Tag im Monat",
            "Jahr": "Tag im Jahr",
        }
        return x[self.time_agg]

    @property
    def period_value(self):
        x = {
            "Jahreszeit": self.main_season,
            "Monat": self.main_month,
            "Jahr": self.main_year,
        }
        return x[self.time_agg]

    @property
    def period_name(self):
        x = {
            "Jahreszeit": cn.season_name[self.main_season],
            "Monat": cn.month_name[self.main_month],
            "Jahr": self.main_year,
        }
        return x[self.time_agg]

    @property
    def time_agg_prefix(self):
        x = {"Jahreszeit": "s", "Monat": "m", "Jahr": "y"}
        return x[self.time_agg]

    @property
    def time_aggregation_parameters(self) -> list:
        x = {
            "Jahreszeit": ["season_year", "season"],
            "Monat": ["year", "month"],
            "Jahr": ["year"],
        }
        return x[self.time_agg]

    @property
    def parameter_label(self):
        return cn.parameters_dict[self.parameter]["label"]

    def show_info(self):
        self.type = "info"
        date_min = self.data.date.min()
        date_max = self.data.date.max()
        min2max = f"{date_min.strftime('%d.%m.%Y')} bis {date_max.strftime('%d.%m.%Y')}"
        st.title("Vivaldi - Die Jahreszeiten-App")
        st.markdown(txt["intro"].format(min2max))
