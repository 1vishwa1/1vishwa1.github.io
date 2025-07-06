import streamlit as st
import pandas as pd
import re
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="Energy Bill Predictor")
st.title("⚡ Electricity Bill Estimator (Simulated)")

st.write("This demo simulates data extraction and prediction based on simplified input without requiring PDF or external pip installs.")

# ---- Simulated Extracted Text ----
simulated_text = """
Service from 07/09/24 - 08/06/24
736 kWh X
Total Amount Due $243.81
average daily electric use was 25.4 kWh
"""

# ---- Field Extraction ----
def extract_field(pattern, text):
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None

billing_start = extract_field(r'Service from (\d{2}/\d{2}/\d{2})', simulated_text)
billing_end = extract_field(r'- (\d{2}/\d{2}/\d{2})', simulated_text)
kwh_used = extract_field(r'(\d+)\s*kWh\s+X', simulated_text)
amount_due = extract_field(r'Total Amount Due\s+\$?(\d+\.\d{2})', simulated_text)
avg_daily_kwh = extract_field(r'average daily\s+electric use was\s+(\d+\.?\d*)\s*kWh', simulated_text)

extracted_data = {
    "Billing Start": billing_start,
    "Billing End": billing_end,
    "kWh Used": kwh_used,
    "Amount Due ($)": amount_due,
    "Avg Daily kWh": avg_daily_kwh
}

st.subheader("Extracted Bill Data")
st.json(extracted_data)

# ---- Prediction Section ----
st.subheader("Predict Next Month's Bill")

month = st.slider("Month", 1, 12, 6)
avg_temp = st.slider("Average Temperature (°C)", -10, 40, 15)
billing_days = st.slider("Billing Days", 25, 35, 30)
usage_kwh = st.slider("kWh Used", 100, 1500, 500)

# ---- Placeholder Training Data ----
df_train = pd.DataFrame({
    'kwh_used': [400, 600, 800],
    'billing_days': [30, 30, 30],
    'avg_temp': [5, 15, 25],
    'month': [1, 6, 8],
    'amount_due': [120, 90, 70]
})

model = RandomForestRegressor(n_estimators=50, random_state=0)
model.fit(df_train[['kwh_used', 'billing_days', 'avg_temp', 'month']], df_train['amount_due'])

pred_input = pd.DataFrame.from_dict([{
    'kwh_used': usage_kwh,
    'billing_days': billing_days,
    'avg_temp': avg_temp,
    'month': month
}])

pred = model.predict(pred_input)[0]
st.metric(label="Predicted Bill Amount", value=f"${pred:.2f}")
