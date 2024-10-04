from openai import OpenAI
import streamlit as st
import pandas as pd
from datetime import datetime
from const import season_name, parameters_dict, time_agg_options, time_agg_prefix
from texts import txt
import json

MODEL = "gpt-4o"
json_file = "./summaries.json"


def get_completion(user_prompt, system_prompt):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        max_tokens=4096,
    )

    return completion.choices[0].message.content.strip()


def get_user_prompt(vivaldi):
    data = get_data(vivaldi)
    year = "" if vivaldi.period_value == "Jahr" else f" {vivaldi.main_year}"
    period = f"{vivaldi.time_agg} {vivaldi.period_value}"  # month, season or year
    user_prompt = txt["user_prompt"].format(
        period=period, year=year, data=data.to_string()
    )
    return user_prompt, data


def get_system_prompt(vivaldi):
    parameters = [
        f"{v['label']}: {v['description']}" for k, v in parameters_dict.items()
    ]
    parameters_expr = "\n".join(parameters)
    ranks = [
        f"rank_{v['label']}: Rang von {v['label']}" for k, v in parameters_dict.items()
    ]
    ranks_expr = "\n".join(ranks)
    period_name = vivaldi.time_agg
    system_prompt = txt["system_prompt"][vivaldi.time_agg].format(
        period_name=period_name, parameters=parameters_expr, ranks=ranks_expr
    )
    return system_prompt


def get_data(vivaldi):
    """
    Retrieves and processes data based on the given time aggregation (season, month, year).

    Args:
        vivaldi: The Vivaldi object containing the necessary parameters.

    Returns:
        summary_table: A processed DataFrame containing the aggregated data.

    """
    agg_parameters = vivaldi.time_aggregation_parameters
    df = vivaldi.data[agg_parameters + list(parameters_dict.keys())]
    df = vivaldi.filter_by_period(df)
    summary_table = (
        df.groupby(agg_parameters)
        .agg({par: parameters_dict[par]["agg_func"] for par in parameters_dict})
        .reset_index()
    )
    summary_table.columns = [
        "_".join(col) if col[1] != None else col[0] for col in summary_table.columns
    ]
    # gererate rankings columns
    for par in [x for x in summary_table.columns if x not in agg_parameters]:
        summary_table["rank_" + par] = summary_table[par].rank(
            ascending=False, method="max"
        )
    summary_table.rename(columns={"year_": "year"}, inplace=True)
    columns_to_delete = [
        x
        for x in ["month_", "season_", "temperature_min", "temperature_max"]
        if x in summary_table.columns
    ]
    summary_table = summary_table.drop(columns_to_delete, axis=1)
    return summary_table


def show(vivaldi):
    if vivaldi.time_agg == "Jahr":
        st.markdown(
            f"**Zusammenfasssung für das Jahr {vivaldi.period_value}** (Generiert mit {MODEL})"
        )
    else:
        st.markdown(
            f"**Zusammenfasssung für den {vivaldi.period_name} {vivaldi.main_year}** (Generiert mit {MODEL})"
        )
    key = f"{vivaldi.time_agg_prefix}-{vivaldi.main_year}-{vivaldi.period_value}"
    # load previous summaries
    with open(json_file, "r") as file:
        data = json.load(file)
    # if the current combination of year and period is found, use it, else show button to generate a summary and store it.
    if key in data:
        response = data[key]
    else:
        response = None
        if st.button("KI-Zusammenfassung"):
            with st.spinner("🤖 Generiert Zusammenfassung..."):
                system_prompt = get_system_prompt(vivaldi)
                user_prompt, tab = get_user_prompt(vivaldi)
                with st.expander("Daten"):
                    st.data_editor(tab)
                response = get_completion(user_prompt, system_prompt)
                data[key] = response
                with open(json_file, "w") as file:
                    json.dump(data, file, indent=4)

    if response:
        cols = st.columns(2)
        with cols[0]:
            st.markdown(response)
