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

def parse_date(date_str, year=1915):
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    cleaned_str = date_str.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
    parts = cleaned_str.split()
    if len(parts) == 2:
        day, month = parts if parts[0].isdigit() else (parts[1], parts[0])
        month = month_map.get(month, None)
        if month and day.isdigit():
            return dt.date(year=int(year), month=int(month), day=int(day))
    return pd.NA

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
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        tooltip="Click me!",
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(icon="cloud")
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


# Show text input box below the map
if st.session_state["prompt"]:
    user_input = st.text_input("Enter your prompt:", placeholder=st.session_state["prompt"])
    if st.button("Submit"):

        # Create a thread for interaction
        thread = client.beta.threads.create()
        thread_id = thread.id  # Store the thread ID to reuse it
        assistant_id = assistant_prop_id

        # Call the assistant with the current message and the stored thread ID
        response = chat_with_assistant(user_input, assistant_id, thread_id)
        print(f"Assistant: {response}")
        
        
        st.write(f"You asked: {user_input}")
        st.write(f"LLM response: {response}")
