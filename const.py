from enum import Enum


class SeasonEnum(Enum):
    WINTER = 1
    SPRING = 2
    SUMMER = 3
    AUTUMN = 4


time_agg_options = ["Monat", "Jahreszeit", "Jahr"]
time_agg_prefix = {1: "m", 2: "s", 3: "y"}
season_id = {"Winter": 1, "Frühling": 2, "Sommer": 3, "Herbst": 4}
season_name = {1: "Winter", 2: "Frühling", 3: "Sommer", 4: "Herbst"}
season_dict = {1: [12, 1, 2], 2: [3, 4, 5], 3: [6, 7, 8], 4: [9, 10, 11]}
month_dict = {
    "Januar": 1,
    "Februar": 2,
    "März": 3,
    "April": 4,
    "Mai": 5,
    "Juni": 6,
    "Juli": 7,
    "August": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Dezember": 12,
}
# climate normal
DEF_NORM_START, DEF_NORM_END = 1991, 2020

month_name = {
    1: "Januar",
    2: "Februar",
    3: "März",
    4: "April",
    5: "Mai",
    6: "Juni",
    7: "Juli",
    8: "August",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Dezember",
}
parameters_dict = {
    "temperature": {
        "label": "Mittl Temperatur",
        "description": "Mittlere Tagestemperatur in °C",
        "unit": "°C",
        "agg_func": ["mean", "min", "max"],
        "frmt": "{:.1f}",
        "exclude_months": [],
        "sort_key": 1,
    },
    "min_temperature": {
        "label": "Min Temperatur",
        "description": "Minimale Tagestemperatur in °C",
        "unit": "°C",
        "agg_func": ["min"],
        "frmt": "{:.1f}",
        "exclude_months": [],
        "sort_key": 2,
    },
    "max_temperature": {
        "label": "Max Temperatur",
        "description": "Maximale Tagestemperatur in °C",
        "unit": "°C",
        "agg_func": ["max"],
        "frmt": "{:.1f}",
        "exclude_months": [],
        "sort_key": 3,
    },
    "hitzetag": {
        "label": "Hitzetage",
        "description": "Anzahl Tage mit einer maximalen Temperatur > 30 °C",
        "unit": "°C",
        "agg_func": ["sum"],
        "frmt": "{:.1f}",
        "exclude_months": [],
        "sort_key": 4,
    },
    "eistag": {
        "label": "Eistage",
        "description": "Anzahl Tage mit einer mittleren Temperatur < 0 °C",
        "unit": "°C",
        "agg_func": ["sum"],
        "frmt": "{:.1f}",
        "exclude_months": [3, 4, 5, 6, 7, 8, 9, 10, 11],
        "sort_key": 5,
    },
    "frosttag": {
        "label": "Frosttage",
        "description": "Anzahl Tage mit einer minimalen Temperatur < 0 °C",
        "unit": "°C",
        "agg_func": ["sum"],
        "frmt": "{:.1f}",
        "exclude_months": [4, 5, 6, 7, 8, 9, 10],
        "sort_key": 6,
    },
    "snowfall": {
        "label": "Schneefall",
        "description": "Schneefallmenge in mm (Niederschlag-Äquivalent)",
        "unit": "mm",
        "agg_func": ["sum"],
        "frmt": "{:.1f}",
        "exclude_months": [5, 6, 7, 8, 9],
        "sort_key": 8,
    },
    "precipitation": {
        "label": "Miederschlag",
        "description": "Niederschlag in mm",
        "unit": "mm",
        "agg_func": ["sum"],
        "frmt": "{:.1f}",
        "exclude_months": [],
        "sort_key": 7,
    },
}

climate_normal_dict = {
    1: [1991, 2020],
    2: [1961, 2090],
    3: [1864, 1960],
    4: [1864, 2020],
}

climate_normal_name_dict = {
    1: "1991-2020",
    2: "1961-2090",
    3: "1864-1960",
    4: "1864-2020",
}

ranking_options = [
    item["label"]
    for item in sorted(parameters_dict.values(), key=lambda x: x["sort_key"])
]

column_names_dict = {v["label"]: k for k, v in parameters_dict.items()}

agg_func_dict = {
    "mean": "Mittelwert",
    "min": "Minimum",
    "max": "Maximum",
    "sum": "Summe",
    "std": "Standardabweichung",
}
