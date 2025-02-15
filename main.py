import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import datetime as dt
import requests

# Function to parse unstructured dates and standardize them
# Dictionary to map month names to numbers
month_map = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
    'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

# Function to parse unstructured dates and standardize them
def parse_date(date_str, year=1915):  # Assuming year 1915
    cleaned_str = date_str.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
    parts = cleaned_str.split()
    if len(parts) == 2:
        if parts[0].isdigit():  # Check if first part is a day
            day, month = parts
        else:
            month, day = parts
        month = month_map.get(month, None)
        if month and day.isdigit():
            return dt.date(year=int(year), month=int(month), day=int(day))
    return pd.NA
df  = pd.read_csv("battles_output.csv")

df["Datetime"] = df.Date.apply(parse_date)

df = df.loc[~df.Location.isna() & ~df.Datetime.isna() & ~df.Latitude.isna() & ~df.Longitude.isna()]


map = folium.Map(location=(52.52437, 13.41053), tiles = "Cartodb Positron",zoom_start=6)#location - the center of the map, zoom_start - the resolution

st.title("Evolution of World War I")

start_date = st.date_input("Start Date", "1915-05-01")
end_date = st.date_input("End Date", "1915-06-30")

print(pd.Timestamp(start_date))

df_selected = df.copy()

print(f'dataframe {type(df_selected.Datetime)}, selector { type(end_date)}')
df_selected = df_selected.loc[(df_selected.Datetime <= end_date) & (df_selected.Datetime >= start_date)]

# Handle user input after clicking the button
if "show_input" not in st.session_state:
    st.session_state.show_input = False
if "clicked_location" not in st.session_state:
    st.session_state.clicked_location = None
if "clicked_location_name" not in st.session_state:  # Initialize clicked_location_name
    st.session_state.clicked_location_name = ""

for _, row in df_selected.iterrows():
    location = [row["Latitude"], row["Longitude"]]
    location_name = row['Location']
    folium.Marker(
        location=location,
        tooltip="Click me!",
        popup=folium.Popup(f"<b>{row['Datetime']}</b><br>{location_name}", max_width=300),
        icon=folium.Icon(icon="cloud"),
    ).add_to(map)

#def callback():
    #st.toast(f"Current zoom: {st.session_state['my_map']['zoom']}")
    #st.toast(f"Current center: {st.session_state['my_map']['center']}")

# call to render Folium map in Streamlit
st_data = st_folium(map, width=725, key="my_map")

# Handle marker click: Show the input box when a marker is clicked
if st_data.get("last_clicked"):
    clicked_location = st_data["last_clicked"]
    st.session_state.clicked_location = clicked_location  # Store the last clicked location
    st.session_state.show_input = True  # Show input box after clicking a marker

# Show the input box if a marker was clicked
if st.session_state.show_input:
    # Ensure the clicked location name is shown correctly
    for _, row in df_selected.iterrows():
        # Compare the coordinates of the clicked marker with the ones from the dataframe
        if (row["Latitude"], row["Longitude"]) == (st_data["last_clicked"]['lat'], st_data["last_clicked"]['lng']):
            st.session_state.clicked_location_name = row["Location"]  # Assign location name correctly
            break  # Stop once the correct location is found
    
    # Ensure that clicked_location_name is correctly displayed in the text input
    user_input = st.text_input(f"Ask a question about the location: {st.session_state.clicked_location_name}")
    if user_input:
        st.write(f"Processing query: {user_input}")  # Here, you can integrate an LLM backend