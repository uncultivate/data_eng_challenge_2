import streamlit as st
import requests
import pandas as pd
import altair as alt

# Set the backend API endpoint
BACKEND_API_URL = 'http://13.236.135.206:5000'

# Fetch coin status
def fetch_coin_status():
    response = requests.get(f'{BACKEND_API_URL}/coin_status')
    if response.status_code == 200:
        return response.json()
    else:
        st.error('Failed to fetch coin status')
        return None

# Fetch price history
def fetch_price_history():
    response = requests.get(f'{BACKEND_API_URL}/price_history')
    if response.status_code == 200:
        return response.json()
    else:
        st.error('Failed to fetch price history')
        return []

# Main UI and Logic
st.title('Challenge #2: Trading Day')

# Investors Overview
st.sidebar.header('Investors Overview')

# Display metrics
coin_status = fetch_coin_status()
if coin_status:
    volume, price, previous_price = coin_status['volume'], coin_status['price'], coin_status['previous_price']
    st.metric("Volume", volume)
    st.metric("Current Price", f"${price:.2f}")
    price_change = price - previous_price
    price_delta = f"${price_change:.2f}" if price_change >= 0 else f"-${abs(price_change):.2f}"
    st.metric("Price Change", price_delta)

# Display price history chart
price_history = fetch_price_history()
if price_history:
    df = pd.DataFrame(price_history, columns=['ID', 'Timestamp', 'Coin Price'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    chart = alt.Chart(df).mark_line(point=True).encode(
        x='Timestamp:T',
        y='Coin Price:Q'
    ).properties(
        title='Coin Price History',
        width=800,
        height=400
    )
    st.altair_chart(chart, use_container_width=True)