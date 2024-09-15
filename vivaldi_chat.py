from openai import OpenAI
import streamlit as st
import pandas as pd
from datetime import datetime
from helper import get_var, get_current_season, season_name
from texte import txt


ranking_options = ['Mittl. Temp', 'Min Temp', 'Max Temp', 'Hitzetage', 'Eistage', 'Frosttage']


def get_completion(user_prompt, df):
    client = OpenAI(
        api_key=get_var("OPENAI_API_KEY"),
    )
    
    df_str = df.to_string(index=False) 
    completion = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {"role": "system", "content": txt['system_prompt'].format(data=df_str)},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        max_tokens=4096,
    )
    
    return completion.choices[0].message.content.strip()
        
    
def show():
    df = st.session_state.data
    
    season_list = list(season_name.keys())
    index = season_list.index(get_current_season())
    selected_season = st.sidebar.selectbox( 
        "Wähle eine Jahreszeit", options=list(season_name.keys()),
        format_func=lambda x: season_name[x],
        index = index
    )
    jahre_options = sorted(df['season_year'].unique(), reverse=True)
    selected_year = st.sidebar.selectbox('Wähle das Jahr aus:', options = jahre_options, index = 0)
    st.markdown(f'**Zusammenfasssung des {season_name[selected_season]}s für das Jahr {selected_year}** (Generiert mit ChatGPT-4o)')
    if st.button('KI-Zusammenfassung'):
        with st.spinner('🤖 Generiert Zusammenfassung...'):
            df = df[df['season'] == selected_season]
            summary_table = df.groupby(['season_year', 'season']).agg({
                'temperature': ['mean'],
                'min_temperature': ['min'],
                'max_temperature': ['max'],
                'hitzetag': ['sum'],
                'frosttag': ['sum'],
                'eistag': ['sum']
            }).reset_index()
            summary_table['rank_mean_temperature'] = summary_table['temperature'].rank(ascending=False, method='max')
            summary_table['rank_max_temperature'] = summary_table['max_temperature'].rank(ascending=False, method='max')
            summary_table['rank_min_temperature'] = summary_table['min_temperature'].rank(ascending=False, method='max')
            user_prompt = txt['user_prompt'].format(season_name[selected_season], selected_year)
            
            response = get_completion(user_prompt, summary_table)
            st.write(response)