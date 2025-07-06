# 📊 Electricity Bill Predictor

This Streamlit app lets you upload multiple past electricity bill PDFs, fetches corresponding weather data, and predicts the next month's bill using a temperature-weighted model.

## Features
- Upload 6+ PDFs of past bills
- Extracts usage and amount due
- Uses historical weather data
- Correlates cold days with higher energy cost
- Predicts next month’s bill based on forecasted temperatures

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
