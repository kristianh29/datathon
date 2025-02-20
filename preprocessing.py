import datetime as dt
import pandas as pd

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

# Function to classify battles into war fronts
def classify_war_front(lat, lon):
    if 45 <= lat <= 53 and -5 <= lon <= 10:  # France, Belgium, Western Germany
        return "Western Front"
    elif 47 <= lat <= 60 and 10 <= lon <= 35:  # Eastern Germany, Poland, Ukraine, Russia
        return "Eastern Front"
    elif 44 <= lat <= 47 and 7 <= lon <= 14:  # Northern Italy, Austria-Hungary
        return "Italian Front"
    elif 38 <= lat <= 45 and 19 <= lon <= 29:  # Serbia, Greece, Bulgaria, Romania
        return "Balkan Front"
    elif 30 <= lat <= 40 and 25 <= lon <= 45:  # Turkey, Palestine, Mesopotamia
        return "Middle Eastern Front"
    elif -35 <= lat <= 10 and -20 <= lon <= 40:  # Africa (approximated)
        return "African Front"
    else:
        return "Unknown Front"

# Define the color mapping for different fronts
front_colors = {
    "Western Front": "blue",
    "Eastern Front": "red",
    "Italian Front": "green",
    "Balkan Front": "purple",
    "Middle Eastern Front": "orange",
    "African Front": "brown",
    "Unknown Front": "gray"
}

import re

def clean_response(text):
    """Remove or replace citation placeholders in the assistant response."""
    return re.sub(r"【\d+:\d+†source】", "", text)  # Remove placeholders