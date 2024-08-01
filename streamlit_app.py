import streamlit as st
import requests
import pandas as pd
import altair as alt
import pytz
from datetime import datetime

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
    
# Fetch investor details
def fetch_investor_deets():
    response = requests.get(f'{BACKEND_API_URL}/investor_deets')
    if response.status_code == 200:
        return response.json()
    else:
        st.error('Failed to fetch investor details')
        return []
    
def fetch_end_time():
    response = requests.get(f'{BACKEND_API_URL}/end_time')
    if response.status_code == 200:
        return response.json()
    else:
        st.error('Failed to fetch investor details')
        return []

# Main UI and Logic
st.title('Challenge #2: Trading Day')
st.divider()

end_time = fetch_end_time()
end_time = datetime.strptime(end_time, "%a, %d %b %Y %H:%M:%S %Z")
# Set the timezone for the original datetime
original_tz = pytz.timezone('GMT') 
localized_time = original_tz.localize(end_time)

# Convert to a different timezone
target_tz = pytz.timezone('Australia/Sydney')
converted_time = localized_time.astimezone(target_tz)
st.sidebar.write(f"End time: {converted_time.time()} AEST")



# Display metrics
coin_status = fetch_coin_status()
if coin_status:
    volume, price, previous_price = coin_status['volume'], coin_status['price'], coin_status['previous_price']
    st.sidebar.header('Investors Overview')
    st.sidebar.write(f"Current coin volume: {volume}")
    col1, col2, col3 = st.columns([1, 6, 3])
    col2.header('Tulip Coin ($TC)')
    col1.image('icon.png')
    price_change = price - previous_price
    price_delta = f"${price_change:.2f}" if price_change >= 0 else f"-${abs(price_change):.2f}"
    col3.metric("Current Price", f"${price:.2f}", price_delta, label_visibility='collapsed')



# Display price history chart
price_history = fetch_price_history()
if price_history:
    df = pd.DataFrame(price_history, columns=['transaction', 'timestamp', 'coin_price'])
    min_price, max_price = df['coin_price'].min(), df['coin_price'].max()
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('transaction:Q', title='Transactions'),
        y=alt.Y('coin_price:Q', title='Coin Price', scale=alt.Scale(domain=[min_price, max_price]), axis=alt.Axis(format='$'))
    ).properties(
        title='Coin Price History',
        width=800,
        height=400
    ).configure_axis(
        grid=False
    ).configure_view(
        strokeOpacity=0
    ).configure(
        background='#0e0e0e',
        title={'color': 'white'},
        axis={'labelColor': 'white', 'titleColor': 'white'}
    )
    
    st.altair_chart(chart, use_container_width=True)

# Investors Overview
investors = fetch_investor_deets()
df = pd.DataFrame(investors, columns=["ID", "Name", "funds", "coins", "strategy"])
# Calculate the total assets
df['Total Assets'] = df['funds'] + df['coins'] * price
df = df.sort_values(by='Total Assets', ascending=False)
# Format the 'total' column as currency
df['Total Assets'] = df['Total Assets'].apply(lambda x: f"${x:.2f}")
df = df[['Name','Total Assets']]
st.sidebar.dataframe(df, hide_index=True, use_container_width=True)