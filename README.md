# 📊 Electricity Bill Forecast with Weather

This Streamlit app lets you upload 6+ electricity bill PDFs, fetches historical temperatures, and predicts your next 2-week bill using current weather forecasts.

## Features
- Auto-extracts billing period, kWh, and cost from PDFs
- Uses Open-Meteo for historical & forecasted temperature
- Trains a model to relate temperature to cost
- Predicts upcoming bill for 14 days ahead

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
