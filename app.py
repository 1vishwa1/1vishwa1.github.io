{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyOfCl8Q+lXhbBAjC5qUqmdz",
      "include_colab_link": True
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/1vishwa1/1vishwa1.github.io/blob/main/app.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "F0EJoEFLHxlx"
      },
      "outputs": [],
      "source": [
        "# Streamlit-compatible fallback version of Energy Bill Predictor (micropip-independent)\n",
        "\n",
        "import streamlit as st\n",
        "import pandas as pd\n",
        "import re\n",
        "from sklearn.ensemble import RandomForestRegressor\n",
        "\n",
        "st.set_page_config(page_title=\"Energy Bill Predictor\")\n",
        "st.title(\"⚡ Electricity Bill Estimator (Simulated)\")\n",
        "\n",
        "st.write(\"This demo simulates data extraction and prediction based on simplified input without requiring PDF or external pip installs.\")\n",
        "\n",
        "# ---- Simulated Extracted Text ----\n",
        "simulated_text = \"\"\"\n",
        "Service from 07/09/24 - 08/06/24\n",
        "736 kWh X\n",
        "Total Amount Due $243.81\n",
        "average daily electric use was 25.4 kWh\n",
        "\"\"\"\n",
        "\n",
        "# ---- Field Extraction ----\n",
        "def extract_field(pattern, text):\n",
        "    match = re.search(pattern, text)\n",
        "    return match.group(1).strip() if match else None\n",
        "\n",
        "billing_start = extract_field(r'Service from (\\d{2}/\\d{2}/\\d{2})', simulated_text)\n",
        "billing_end = extract_field(r'- (\\d{2}/\\d{2}/\\d{2})', simulated_text)\n",
        "kwh_used = extract_field(r'(\\d+)\\s*kWh\\s+X', simulated_text)\n",
        "amount_due = extract_field(r'Total Amount Due\\s+\\$?(\\d+\\.\\d{2})', simulated_text)\n",
        "avg_daily_kwh = extract_field(r'average daily\\s+electric use was\\s+(\\d+\\.?\\d*)\\s*kWh', simulated_text)\n",
        "\n",
        "extracted_data = {\n",
        "    \"Billing Start\": billing_start,\n",
        "    \"Billing End\": billing_end,\n",
        "    \"kWh Used\": kwh_used,\n",
        "    \"Amount Due ($)\": amount_due,\n",
        "    \"Avg Daily kWh\": avg_daily_kwh\n",
        "}\n",
        "\n",
        "st.subheader(\"Extracted Bill Data\")\n",
        "st.json(extracted_data)\n",
        "\n",
        "# ---- Prediction Section ----\n",
        "st.subheader(\"Predict Next Month's Bill\")\n",
        "\n",
        "month = st.slider(\"Month\", 1, 12, 6)\n",
        "avg_temp = st.slider(\"Average Temperature (°C)\", -10, 40, 15)\n",
        "billing_days = st.slider(\"Billing Days\", 25, 35, 30)\n",
        "usage_kwh = st.slider(\"kWh Used\", 100, 1500, 500)\n",
        "\n",
        "# ---- Placeholder Training Data ----\n",
        "df_train = pd.DataFrame({\n",
        "    'kwh_used': [400, 600, 800],\n",
        "    'billing_days': [30, 30, 30],\n",
        "    'avg_temp': [5, 15, 25],\n",
        "    'month': [1, 6, 8],\n",
        "    'amount_due': [120, 90, 70]\n",
        "})\n",
        "\n",
        "model = RandomForestRegressor(n_estimators=50, random_state=0)\n",
        "model.fit(df_train[['kwh_used', 'billing_days', 'avg_temp', 'month']], df_train['amount_due'])\n",
        "\n",
        "pred_input = pd.DataFrame.from_dict([{\n",
        "    'kwh_used': usage_kwh,\n",
        "    'billing_days': billing_days,\n",
        "    'avg_temp': avg_temp,\n",
        "    'month': month\n",
        "}])\n",
        "\n",
        "pred = model.predict(pred_input)[0]\n",
        "st.metric(label=\"Predicted Bill Amount\", value=f\"${pred:.2f}\")\n"
      ]
    }
  ]
}
