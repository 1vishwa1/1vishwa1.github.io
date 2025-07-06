import streamlit as st
import pandas as pd
import numpy as np
import requests
import re
import pdfplumber
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="Electricity Bill Forecast", layout="centered")
st.title("⚡ Predict Upcoming Electricity Bill Using Weather & Past Bills")

st.markdown("""Upload at least **6 recent electricity bill PDFs**. This app:
- Extracts your energy usage and cost
- Fetches daily weather data for those billing periods
- Assumes colder days → more consumption
- Predicts next 2 weeks' bill using temperature forecast
- This tool works for the Boston region
- Head to https://www.vbadiger.com for more such cool projects""")

uploaded_files = st.file_uploader("Upload at least 6 electricity bill PDFs", type="pdf", accept_multiple_files=True)

# --- Utilities ---
def extract_bill_data(file):
    with pdfplumber.open(file) as pdf:
        text = ''.join(page.extract_text() for page in pdf.pages if page.extract_text())

    try:
        billing_period = re.search(r'Service from (\d{2}/\d{2}/\d{2}) - (\d{2}/\d{2}/\d{2})', text)
        kwh_used = re.search(r'(\d+)\s*kWh\s+X', text)
        amount_due = re.search(r'Total Amount Due\s+\$?(\d+\.\d{2})', text)

        start = pd.to_datetime(billing_period.group(1), format="%m/%d/%y")
        end = pd.to_datetime(billing_period.group(2), format="%m/%d/%y")
        usage = int(kwh_used.group(1))
        cost = float(amount_due.group(1))
        return {'billing_start': start, 'billing_end': end, 'kwh_used': usage, 'total_amount_due': cost}
    except:
        return None

def fetch_weather(start, end):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 42.3601,
        "longitude": -71.0589,
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d"),
        "daily": "temperature_2m_mean",
        "timezone": "America/New_York"
    }
    res = requests.get(url, params=params)
    return pd.DataFrame(res.json()['daily'])

def forecast_next_2_weeks():
    today = datetime.now().date()
    start = today + timedelta(days=1)
    end = start + timedelta(days=13)  # forecast 14 days ahead

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 42.3601,
        "longitude": -71.0589,
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d"),
        "daily": "temperature_2m_mean",
        "timezone": "America/New_York"
    }
    res = requests.get(url, params=params)
    json_data = res.json()
    if "daily" not in json_data:
        st.error("⚠️ Forecast API failed. Check your internet or API availability.")
        return pd.DataFrame(columns=["date", "temperature_2m_mean"])

    df = pd.DataFrame(json_data["daily"])
    df["date"] = pd.to_datetime(df["time"])
    return df[["date", "temperature_2m_mean"]]

# --- Main Pipeline ---
if uploaded_files and len(uploaded_files) >= 6:
    all_daily_data = []
    for file in uploaded_files:
        bill = extract_bill_data(file)
        if not bill:
            st.warning(f"⚠️ Could not parse {file.name}")
            continue

        weather_df = fetch_weather(bill['billing_start'], bill['billing_end'])
        weather_df['date'] = pd.to_datetime(weather_df['time'])
        weather_df = weather_df[['date', 'temperature_2m_mean']]
        weather_df['inv_temp'] = 1 / (weather_df['temperature_2m_mean'] + 0.01)
        weather_df['weight'] = weather_df['inv_temp'] / weather_df['inv_temp'].sum()
        weather_df['kwh_used'] = weather_df['weight'] * bill['kwh_used']
        weather_df['cost'] = weather_df['weight'] * bill['total_amount_due']
        all_daily_data.append(weather_df[['date', 'temperature_2m_mean', 'kwh_used', 'cost']])

    full_df = pd.concat(all_daily_data).dropna()
    full_df['month'] = full_df['date'].dt.month

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(full_df[['temperature_2m_mean', 'month']], full_df['cost'])

    forecast_df = forecast_next_2_weeks()
    if not forecast_df.empty:
            forecast_df['month'] = forecast_df['date'].dt.month
            forecast_df['predicted_cost'] = model.predict(forecast_df[['temperature_2m_mean', 'month']])
            total_predicted = forecast_df['predicted_cost'].sum() * 2
            st.markdown(f"""
                <div style='background-color:#d1e7dd;padding:40px;border-radius:12px;text-align:center;border:3px solid #0f5132;'>
                    <h1 style='color:#0f5132;font-size:36px;'>📅 Predicted Bill for Next Month:</h1>
                    <h1 style='color:#14532d;font-size:56px;'>${total_predicted:.2f}</h1>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Could not get weather forecast. Please try again later or ⚠️ Upload at least 6 valid PDF files to run prediction.")    
