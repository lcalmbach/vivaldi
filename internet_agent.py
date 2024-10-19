import streamlit as st
from langchain.adapters.openai import convert_openai_messages
from langchain_community.chat_models import ChatOpenAI
from tavily import TavilyClient

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]

class InternetSearchAgent():
    def __init__(self, intervall_of_interest, period_name, year):
        self.intervall_of_interest = intervall_of_interest
        self.period_name = period_name
        self.year = year
        self.client = TavilyClient(api_key=TAVILY_API_KEY)

    def run(self):
        query = f"Schreibe eine Zusammenfassung zum Wetter im {self.intervall_of_interest} {self.period_name} im Jahr {self.year} in der Schweiz. War es signifikant anders als in anderen Jahren? Gab es signifikante Ereignisse? Wie ist diese Jahreszeit mit historischen Daten vergleichbar?"
        content = self.client.search(query, search_depth="advanced")["results"]
        prompt = [{
            "role": "system",
            "content":  f'Du bist ein Wetter Experte und fasst das Wetter einer {self.intervall_of_interest} zusammen in einem kurzen Artikel'\
                        f'Bei allen Zitaten in deinem Text erwähnst du die Quelle als verlinkte URL.'\
                        f'Halte die Zusamenfassung kurz und prägnant.'
        }, {
            "role": "user",
            "content": f'Information: """{content}"""\n\n' \
                    f'Using the above information and answer the following'\
                    f'query: "{query}" in a summary report --'\
                    f'Please use MLA format and markdown syntax.'
        }]
        lc_messages = convert_openai_messages(prompt)
        report = ChatOpenAI(model='gpt-4o',openai_api_key=OPENAI_API_KEY).invoke(lc_messages).content
        return report

        