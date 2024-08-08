import streamlit as st
from streamlit_autorefresh import st_autorefresh
import requests
import pandas as pd
import altair as alt
import pytz
from datetime import datetime

st.set_page_config(
    page_title="Tulip Coin",
    page_icon="🌷",
)

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
end_time = fetch_end_time()
end_time = datetime.strptime(end_time, "%a, %d %b %Y %H:%M:%S %Z")
now = datetime.now()

# Set the timezone for the original datetime
original_tz = pytz.timezone('GMT') 
localized_end_time = original_tz.localize(end_time)

# Convert to a different timezone
target_tz = pytz.timezone('Australia/Sydney')
converted_end_time = localized_end_time.astimezone(target_tz)
converted_current = now.astimezone(target_tz)

st.sidebar.write(f"End time: {converted_end_time.time()} AEST")
auto_refresh = converted_current < converted_end_time
if auto_refresh:
    count = st_autorefresh(interval=5000, limit=100)




# Display metrics
coin_status = fetch_coin_status()
if coin_status:
    volume, price, previous_price = coin_status['volume'], coin_status['price'], coin_status['previous_price']
    st.sidebar.header('Investor Leaderboard')
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
    df = pd.DataFrame(price_history, columns=['transaction', 'timestamp', 'coin_price', 'name', 'coins', 'funds', 'type'])
    # Add a new column for index + 1
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

    # Display transactions table
    st.markdown("__Order Book__")
    # Create 'previous_price' column
    df['previous_price'] = df['coin_price'].shift(1)

    # Convert the 'timestamp' column to datetime and set timezone to GMT
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize('GMT')

    # Convert the timezone from GMT to AEST
    df['timestamp'] = df['timestamp'].dt.tz_convert('Australia/Sydney')

    # Extract the time component
    df['time'] = df['timestamp'].dt.strftime('%H:%M:%S')

    # Select and rename columns
    orderbook_df = df[['time', 'name', 'coins', 'previous_price', 'funds', 'type']].rename(
        columns={
            'time': 'Time',
            'type': 'Type',
            'name': 'Name',
            'coins': 'Amount',
            'previous_price': 'Price',
            'funds': 'Total',

        }
    ).sort_values(by='Time', ascending=False).tail(100)[['Time', 'Name', 'Type', 'Amount', 'Price', 'Total']]

    def highlight_type(s):
        if s.Type =='buy':
            return ['background-color: #01421d']*len(s)
        elif s.Type == 'sell':
            return ['background-color: #3d0003']*len(s)
        else:
            return [''] * len(s)  # Return a list of empty styles if no condition is met


    # Format the 'Previous_Price' and 'Total' columns as currency
    orderbook_df['Price'] = orderbook_df['Price'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "N/A")
    orderbook_df['Total'] = orderbook_df['Total'].apply(lambda x: f"${x:,.2f}")
    orderbook_df = orderbook_df.iloc[0:-1]
    orderbook_df = orderbook_df.style.apply(highlight_type, axis=1)         
    st.dataframe(orderbook_df, hide_index=True, use_container_width=True)

# Investors Leaderboard
if coin_status:
    investors = fetch_investor_deets()
    df = pd.DataFrame(investors, columns=["ID", "Name", "Funds", "Coins", "strategy"])
    # Calculate the total assets
    df['Total Assets'] = df['Funds'] + df['Coins'] * price
    df = df.sort_values(by='Total Assets', ascending=False).reset_index(drop=True)
    for index, row in df.iterrows():
    # Make the first line bold
        st.sidebar.markdown(f"**{index + 1}: {row['Name']}**")
        # Convert 'Funds' and 'Total Assets' to float and format them as currency
        formatted_funds = f"${float(row['Funds']):,.2f}"
        formatted_total_assets = f"${float(row['Total Assets']):,.2f}"
        
        # Insert the values into a one-line table with 75% font size
        st.sidebar.markdown(f"""
        <table style='font-size:85%;'>
            <tr>
                <th style='text-align:center;'>Coins</th>
                <th style='text-align:center;'>Funds</th>
                <th style='text-align:center;'>Total</th>
            </tr>
            <tr>
                <td style='text-align:center;'>{row['Coins']}</td>
                <td style='text-align:center;'>{formatted_funds}</td>
                <td style='text-align:center;'>{formatted_total_assets}</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
