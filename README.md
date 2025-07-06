# 📊 Streamlit Weather-Based Energy Bill Predictor

This app lets you upload 6+ past electricity bill PDFs and predicts your next monthly bill using:
- Daily weather data during each billing period
- A Random Forest model that correlates colder days with higher costs
- Open-Meteo API to forecast the next 2 weeks and extrapolates it for a full month

## Features
- PDF file uploader (6+ files required)
- Big Run/New Prediction button for interactivity
- Flashy output card for monthly bill prediction
- Ready to deploy on Streamlit Cloud

## To Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
