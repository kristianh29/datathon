from preprocessing import parse_date, classify_war_front, front_colors, clean_response
import os
import re
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import datetime as dt
import openai
from openai import OpenAI
from dotenv import load_dotenv

# Import LLM backend
from assistants import chat_with_assistant
load_dotenv()

st.set_page_config(layout='wide')
client = OpenAI(api_key=os.getenv("API_KEY"))

assistant_prop_id = "asst_ufufmyqiucnAgWcq6nks0Jf8"
assistant_ww1exp_id = "asst_z3kMZJUvk2KKaShwgG6pijSP"

# Load and process the dataset
df = pd.read_csv("battles_output_final.csv", encoding='unicode_escape')
df["Datetime"] = df.Date.apply(parse_date)
df = df.dropna(subset=["Location", "Datetime", "Latitude", "Longitude"])

# Streamlit App UI
st.title("Evolution of World War I")
start_date = st.date_input("Start Date", dt.date(1915, 5, 1))
end_date = st.date_input("End Date", dt.date(1915, 6, 30))
df_selected = df[(df.Datetime >= start_date) & (df.Datetime <= end_date)]

# Folium Map
map = folium.Map(location=(52.52437, 13.41053), tiles="Cartodb Positron", zoom_start=6, control_scale=False)

for _, row in df_selected.iterrows():
    location_name = row["Location"]
    popup_text = f'{row["Datetime"]}<br>{location_name}'
    
    front = classify_war_front(row["Latitude"], row["Longitude"])  # Determine  front based on lat/lon
    color = front_colors[front]  # Get corresponding color
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        tooltip="Click me!",
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(color=color, icon="skull", prefix="fa")
    ).add_to(map)

# Display Folium map
st_data = st_folium(map, width=2000, height=500, key="my_map")

# Initialize session states
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""
if "response_prop" not in st.session_state:
    st.session_state["response_prop"] = ""
if "response_factual" not in st.session_state:
    st.session_state["response_factual"] = ""
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = None

# Text input form
with st.form(key="chat_form"):
    user_input = st.text_input("Enter your prompt:", placeholder="Ask me a question about World War I")
    submit_button = st.form_submit_button("Submit")
    st.session_state["response_factual"] = None

if submit_button and user_input.strip():
    st.session_state["user_input"] = user_input  # Store input
    
    # Create a thread for interaction (only create a new thread if it doesn't exist)
    if not st.session_state["thread_id"]:
        thread = client.beta.threads.create()
        st.session_state["thread_id"] = thread.id  # Store thread ID to reuse it

    # Get response from the propaganda assistant
    st.session_state["response_prop"] = clean_response(chat_with_assistant(user_input, assistant_prop_id, st.session_state["thread_id"]))

# Display stored responses
if st.session_state["user_input"]:
    st.write(f"**You asked:** {st.session_state['user_input']}")
if st.session_state["response_prop"]:
    st.write(f"🟥 **Propaganda Assistant:** {st.session_state['response_prop']}")

    # Second form for factual response
    with st.form(key="chat_form_2"):
        response_button = st.form_submit_button("Click here for a factual response regarding the information above")

    if response_button and st.session_state["response_prop"]:
        prompt = f'User asked {st.session_state["user_input"]}, and the German-biased assistant answered {st.session_state["response_prop"]}. Use the system instructions to critique this output'
        st.session_state["response_factual"] = clean_response(chat_with_assistant(prompt, assistant_ww1exp_id, st.session_state["thread_id"]))

# Display factual assistant response
if st.session_state["response_factual"]:
    st.write(f"🟦 **Factual Assistant:** {st.session_state['response_factual']}")
