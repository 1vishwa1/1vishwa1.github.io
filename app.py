import streamlit as st
import pandas as pd
import numpy as np
import requests
import re
import pdfplumber
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="Electricity Bill Forecast", layout="centered")
st.title("⚡ Predict Next Month's Electricity Bill Based on Past Bills + Weather")

st.markdown("""Upload at least **6 recent electricity bill PDFs**. The app will:
- Extract billing periods and total usage
- Fetch daily weather during each period
- Correlate temperature to cost (colder = costlier)
- Predict next month’s bill based on temperature forecast""")

uploaded_files = st.file_uploader("Upload Electricity Bill PDFs", type="pdf", accept_multiple_files=True)

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

def forecast_next_month_temperatures():
    today = datetime.now().date()
    next_month = today.replace(day=1) + timedelta(days=32)
    start = next_month.replace(day=1)
    end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    url = "https://archive-api.open-meteo.com/v1/era5"
    params = {
        "latitude": 42.3601,
        "longitude": -71.0589,
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d"),
        "daily": "temperature_2m_mean",
        "timezone": "America/New_York"
    }
    res = requests.get(url, params=params)
    df = pd.DataFrame(res.json()['daily'])
    df['date'] = pd.to_datetime(df['time'])
    return df[['date', 'temperature_2m_mean']]

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

    forecast_df = forecast_next_month_temperatures()
    forecast_df['month'] = forecast_df['date'].dt.month
    forecast_df['predicted_cost'] = model.predict(forecast_df[['temperature_2m_mean', 'month']])

    total_predicted = forecast_df['predicted_cost'].sum()

    st.success(f"📅 Predicted Bill for Next Month: **${total_predicted:.2f}**")
else:
    st.info("Please upload at least 6 readable PDF bills to generate a prediction.")
