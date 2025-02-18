from preprocessing import parse_date, classify_war_front, front_colors
import os

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import datetime as dt
import openai
from openai import OpenAI
from dotenv import load_dotenv, dotenv_values
#import our LLM backend here
from assistants import chat_with_assistant
load_dotenv()
client = OpenAI(api_key=os.getenv("API_KEY"))

assistant_prop_id = "asst_ufufmyqiucnAgWcq6nks0Jf8"
assistant_ww1exp_id = "asst_z3kMZJUvk2KKaShwgG6pijSP"

# Load and process the dataset
df = pd.read_csv("battles_output.csv")
df["Datetime"] = df.Date.apply(parse_date)
df = df.dropna(subset=["Location", "Datetime", "Latitude", "Longitude"])

# Streamlit App UI
st.title("Evolution of World War I")
start_date = st.date_input("Start Date", dt.date(1915, 5, 1))
end_date = st.date_input("End Date", dt.date(1915, 6, 30))
df_selected = df[(df.Datetime >= start_date) & (df.Datetime <= end_date)]

# Folium Map
map = folium.Map(location=(52.52437, 13.41053), tiles="Cartodb Positron", zoom_start=6)

for _, row in df_selected.iterrows():
    location_name = row["Location"]
    popup_text = f'{row["Datetime"]}<br>{location_name}'
    
    front = classify_war_front(row["Latitude"], row["Longitude"])  # Determine front based on lat/lon
    color = front_colors[front]  # Get corresponding color
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        tooltip="Click me!",
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(color=color, icon="skull", prefix = "fa")
    ).add_to(map)



# Display Folium map
st_data = st_folium(map, width=725, key="my_map")



# Initialize session state for prompt
if "prompt" not in st.session_state:
    st.session_state["prompt"] = ""
if "last_clicked" not in st.session_state:
    st.session_state["last_clicked"] = None

# Check if a marker was clicked
if st_data.get("last_clicked") != st.session_state["last_clicked"]:
    st.session_state["last_clicked"] = st_data.get("last_clicked")
    st.session_state["prompt"] = "Ask me a question about this battle"

#Text input is always visible now
with st.form(key="chat_form"):
    user_input = st.text_input("Enter your prompt:", placeholder="Ask me a question about World War I")
    submit_button = st.form_submit_button("Submit")  # Keeps the button visible

if submit_button and user_input.strip():
    # Create a thread for interaction
    thread = client.beta.threads.create()
    thread_id = thread.id  # Store the thread ID to reuse it

    #Get response from the propaganda assistant
    response_prop = chat_with_assistant(user_input, assistant_prop_id, thread_id)

    #Get response from the factual assistant
    response_factual = chat_with_assistant(user_input, assistant_ww1exp_id, thread_id)

    #Display responses
    st.write(f"**You asked:** {user_input}")
    st.write(f"🟥 **Propaganda Assistant:** {response_prop}")
    st.write(f"🟦 **Factual Assistant:** {response_factual}")