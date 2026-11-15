import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import plotly.graph_objects as go
from datetime import date

st.set_page_config(page_title="Nepal Climate & Forecast Assistant", layout="wide")

# --- 1. Load Data & Train Models (Cached for instant interactivity) ---
DATASETS = {
    "Rasuwa (High Mountain)": "https://raw.githubusercontent.com/hamnanadeem450-jpg/NASA-Earth-System-Trend-Detective/main/data/processed/rasuwa_climate_cleaned.csv",
    "Dhankuta (Mid-Hill)": "https://raw.githubusercontent.com/hamnanadeem450-jpg/NASA-Earth-System-Trend-Detective/main/data/processed/dhankuta_climate_cleaned.csv"
}

@st.cache_resource
def load_and_train_models(city_url):
    df = pd.read_csv(city_url)
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    # Daily Temperature Model
    df_temp = df[['DATE', 'T2M']].dropna().rename(columns={'DATE': 'ds', 'T2M': 'y'})
    m_temp = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    m_temp.fit(df_temp)
    
    # Monthly Precipitation Model (for reliable seasonal rain planning)
    df_rain_m = (
        df.set_index('DATE')['PRECTOTCORR']
        .resample('MS').sum().reset_index()
        .rename(columns={'DATE': 'ds', 'PRECTOTCORR': 'y'})
    )
    m_rain = Prophet(yearly_seasonality=True, seasonality_mode='multiplicative')
    m_rain.fit(df_rain_m)
    
    return df, m_temp, m_rain

# --- Sidebar Controls ---
st.sidebar.header("🌍 Location & Settings")
selected_city = st.sidebar.selectbox("Select District", list(DATASETS.keys()))
forecast_years = st.sidebar.slider("Forecast Horizon (Years)", 1, 5, 3)

with st.spinner(f"Training AI forecasting models for {selected_city}..."):
    raw_df, temp_model, rain_model = load_and_train_models(DATASETS[selected_city])

# --- Main Header ---
st.title("🌦️ Nepal Smart Climate & Forecast Assistant")
st.markdown(f"Interactive AI weather & seasonal planner for **{selected_city}** powered by NASA Earth System data (2000–2025) & Prophet.")

# Create Tabs for Practical Daily Use vs. Trend Exploration
tab1, tab2, tab3 = st.tabs([
    "📅 Date & Trip Weather Predictor", 
    "🌱 Best Month & Activity Finder", 
    "📈 Long-Term Climate Trends"
])

# ==========================================
# TAB 1: Interactive Date Predictor
# ==========================================
with tab1:
    st.subheader("Check Expected Weather for Any Future Date")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        target_date = st.date_input(
            "Select a Date (2026–2030)",
            value=date(2026, 10, 15),
            min_value=date(2026, 1, 1),
            max_value=date(2030, 12, 31)
        )
        temp_anomaly = st.slider("What-If Warming Scenario (°C)", 0.0, 2.5, 0.0, 0.1)

    # Predict for selected date
    future_single = pd.DataFrame({'ds': [pd.to_datetime(target_date)]})
    pred_t = temp_model.predict(future_single).iloc[0]
    
    month_start = pd.to_datetime(target_date).replace(day=1)
    pred_r = rain_model.predict(pd.DataFrame({'ds': [month_start]})).iloc[0]
    
    est_temp = pred_t['yhat'] + temp_anomaly
    est_rain_month = max(0.0, pred_r['yhat'])

    # Practical Advisory Logic
    if est_rain_month > 250:
        rain_status = "High Monsoon Rain Risk 🌧️"
        advice = "Heavy seasonal rainfall expected. Expect wet trails, potential road delays, and high soil moisture."
    elif est_rain_month > 80:
        rain_status = "Moderate / Transitional Rain 🌦️"
        advice = "Occasional showers likely. Carry rain gear; good conditions for agriculture."
    else:
        rain_status = "Dry & Clear Conditions ☀️"
        advice = "Low rainfall probability. Ideal window for trekking, outdoor construction, and travel."

    with col2:
        m1, m2, m3 = st.columns(3)
        m1.metric("Expected Temperature", f"{est_temp:.1f} °C", f"Range: {pred_t['yhat_lower']+temp_anomaly:.1f}° to {pred_t['yhat_upper']+temp_anomaly:.1f}°C")
        m2.metric("Monthly Rainfall Outlook", f"{est_rain_month:.0f} mm", rain_status)
        m3.metric("Comfort Level", "Cold" if est_temp < 10 else ("Warm" if est_temp > 22 else "Mild / Pleasant"))
        st.info(f"**Daily Life Recommendation:** {advice}")

# ==========================================
# TAB 2: Best Month & Activity Finder
# ==========================================
with tab2:
    st.subheader("Find the Best Months for Your Activity")
    c1, c2 = st.columns(2)
    target_year = c1.selectbox("Select Target Year", [2026, 2027, 2028, 2029, 2030])
    goal = c2.selectbox("What are you planning?", [
        "Trekking & Outdoor Travel (Dry & Mild)",
        "Agriculture / High Water Availability (Peak Monsoon)",
        "Solar Energy / Clear Sky Operations (Driest Months)"
    ])

    months_df = pd.DataFrame({'ds': pd.date_range(f"{target_year}-01-01", f"{target_year}-12-01", freq='MS')})
    t_yr = temp_model.predict(months_df)
    r_yr = rain_model.predict(months_df)

    summary = pd.DataFrame({
        "Month": months_df['ds'].dt.strftime('%B'),
        "Avg Temp (°C)": t_yr['yhat'].round(1),
        "Expected Rainfall (mm)": r_yr['yhat'].clip(lower=0).round(0)
    })

    if "Trekking" in goal:
        ranked = summary.sort_values(by=["Expected Rainfall (mm)", "Avg Temp (°C)"], ascending=[True, False]).head(4)
        st.success(f"Top Recommended Months for **Trekking & Travel** in {target_year}:")
    elif "Agriculture" in goal:
        ranked = summary.sort_values(by="Expected Rainfall (mm)", ascending=False).head(4)
        st.success(f"Peak Water / Monsoon Months for **Agriculture** in {target_year}:")
    else:
        ranked = summary.sort_values(by="Expected Rainfall (mm)", ascending=True).head(4)
        st.success(f"Driest Months for **Clear-Sky Operations** in {target_year}:")

    st.dataframe(ranked, use_container_width=True, hide_index=True)

# ==========================================
# TAB 3: Interactive Forecast Charts
# ==========================================
with tab3:
    st.subheader(f"Temperature & Rainfall Projections ({2026}–{2025 + forecast_years})")
    metric_choice = st.radio("Select Variable to Visualize", ["Temperature (°C)", "Monthly Rainfall (mm)"], horizontal=True)

    if metric_choice == "Temperature (°C)":
        future_df = temp_model.make_future_dataframe(periods=forecast_years * 365, freq='D')
        fc = temp_model.predict(future_df)
        fc_recent = fc[fc['ds'] >= '2023-01-01']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fc_recent['ds'], y=fc_recent['yhat'], name='Predicted Temp', line=dict(color='#ff6b35')))
        fig.add_trace(go.Scatter(
            x=pd.concat([fc_recent['ds'], fc_recent['ds'][::-1]]),
            y=pd.concat([fc_recent['yhat_upper'], fc_recent['yhat_lower'][::-1]]),
            fill='toself', fillcolor='rgba(255, 107, 53, 0.2)', line=dict(color='rgba(255,255,255,0)'),
            name='Confidence Range'
        ))
        fig.update_layout(yaxis_title="Temperature (°C)", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        future_m = rain_model.make_future_dataframe(periods=forecast_years * 12, freq='MS')
        fc_m = rain_model.predict(future_m)
        fc_m_recent = fc_m[fc_m['ds'] >= '2020-01-01']
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=fc_m_recent['ds'], y=fc_m_recent['yhat'].clip(lower=0), name='Monthly Rainfall (mm)', marker_color='#2b8cbe'))
        fig.update_layout(yaxis_title="Monthly Total Rainfall (mm)", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
