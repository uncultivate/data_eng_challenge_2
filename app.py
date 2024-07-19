import streamlit as st
import sqlite3
from datetime import datetime, timedelta, time as timed
import time
import pytz
import altair as alt
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Database Initialization
def init_db():
    conn = sqlite3.connect('coin_price_history.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            coin_price REAL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS investors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            funds REAL,
            coins INTEGER,
            strategy TEXT,
            timestamp TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS coin_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            volume INTEGER,
            price REAL,
            previous_price REAL
        )
    ''')
    conn.commit()
    return conn, c

conn, c = init_db()

# Initial settings
initial_coin_volume = 100000
initial_coin_price = 0.1
k = initial_coin_volume * initial_coin_price
n_investors = 5

# Function to log the price in the database
def log_price(price):
    timestamp = datetime.now()
    c.execute('INSERT INTO price_history (timestamp, coin_price) VALUES (?, ?)', (timestamp, price))
    conn.commit()

# Function to get the latest coin status
def get_coin_status():
    c.execute('SELECT volume, price, previous_price FROM coin_status ORDER BY id DESC LIMIT 1')
    return c.fetchone()

# Function to update coin status
def update_coin_status(volume, price, previous_price):
    c.execute('INSERT INTO coin_status (volume, price, previous_price) VALUES (?, ?, ?)', (volume, price, previous_price))
    conn.commit()

# Initialize the coin status if it does not exist
if not get_coin_status():
    update_coin_status(initial_coin_volume, initial_coin_price, initial_coin_price)
    log_price(initial_coin_price)

# Function to add a new investor
def add_investor(name, funds, strategy, timestamp):
    c.execute('INSERT INTO investors (name, funds, coins, strategy, timestamp) VALUES (?, ?, 0, ?, ?)', (name, funds, strategy, timestamp))
    conn.commit()

# Function to get list of investors
def get_investors():
    c.execute('SELECT id, name FROM investors')
    return c.fetchall()

# Function to get investor details
def get_investor_details(investor_id):
    c.execute('SELECT funds, coins, strategy FROM investors WHERE id = ?', (investor_id,))
    return c.fetchone()

# Function to update investor details
def update_investor(investor_id, funds, coins):
    timestamp = datetime.now()
    c.execute('UPDATE investors SET funds = ?, coins = ?, timestamp = ? WHERE id = ?', (funds, coins, timestamp, investor_id))
    conn.commit()

# Function to select current investor
def select_current_investor():
    c.execute('SELECT id, timestamp FROM investors ORDER BY timestamp ASC')
    result =  c.fetchone()
    if result:
        return result[0] # Extract the id value from the tuple
    return None  # Handle case where no rows are returned

def adjusted_datetime(dt, seconds):
    return dt - timedelta(seconds=seconds)

# Functions to handle buying and selling of coins
def buy_coins(investor_id, num_coins, current_price):
    funds, coins, _ = get_investor_details(investor_id)
    total_cost = num_coins * current_price
    if total_cost <= funds:
        funds -= total_cost
        coins += num_coins
        volume, price, previous_price = get_coin_status()
        volume -= num_coins
        new_price = k / volume  # y = k/x
        update_coin_status(volume, new_price, price)
        update_investor(investor_id, funds, coins)
        log_price(new_price)
        return f'Bought {num_coins} coins at ${current_price:.2f} each'
    return 'Hold: No action taken'

def sell_coins(investor_id, num_coins, current_price):
    funds, coins, _ = get_investor_details(investor_id)
    if num_coins <= coins:
        total_revenue = num_coins * current_price
        funds += total_revenue
        coins -= num_coins
        volume, price, previous_price = get_coin_status()
        volume += num_coins
        new_price = k / volume  # y = k/x
        update_coin_status(volume, new_price, price)
        update_investor(investor_id, funds, coins)
        log_price(new_price)
        return f'Sold {num_coins} coins at ${current_price:.2f} each'
    return 'Hold: No action taken'

# Function to get price history
def get_price_history():
    c.execute('SELECT id, coin_price FROM price_history')
    return c.fetchall()

# Function to get the strategy function by name
def get_strategy_function(strategy_name):
    strategies = {
        'strategy_1': strategy_1,
        'strategy_2': strategy_2,
        'strategy_3': strategy_3,
        'strategy_4': strategy_4
    }
    return strategies.get(strategy_name)

# Define strategies
def strategy_1(df):
    if len(df) < 5:
        return 'buy', 0.5
    elif len(df) <= 20:
        return 'buy', 0.2 
    last_price = df['coin_price'].iloc[-1]
    if len(df) > 20:
        return 'sell', 1
    return 'buy', 0.4

def strategy_2(df):
    if len(df) < 2:
        return 'sell', 0.5
    last_price = df['coin_price'].iloc[-1]
    second_last_price = df['coin_price'].iloc[-2]
    price_change = (last_price - second_last_price) / second_last_price
    if price_change > 0.02:
        return 'sell', 0.5
    elif price_change < 0:
        return 'buy', 0.5
    return 'hold', 0.0

def strategy_3(df):
    if len(df) < 5:
        return 'buy', 0.1
    last_price = df['coin_price'].iloc[-1]
    last_five_prices = df['coin_price'].iloc[-5:]
    if last_price == last_five_prices.max():
        return 'sell', 0.5
    elif last_price == last_five_prices.min():
        return 'buy', 0.5
    return 'hold', 0.0

def strategy_4(df):
    if len(df) > 10:
        return 'buy', 0.5
    return 'hold', 0.0

# Main UI and Logic
st.title('Challenge #2: Trading Day')

# Sidebar Buttons


if st.sidebar.button('Reset'):
    c.execute('DROP TABLE IF EXISTS investors')
    c.execute('DROP TABLE IF EXISTS price_history')
    c.execute('DROP TABLE IF EXISTS coin_status')
    init_db()
    # Get the current datetime
    current_time = datetime.now()

    add_investor('Whale', 10000, 'strategy_1', adjusted_datetime(current_time, 4))
    add_investor('Jono', 10000, 'strategy_1', adjusted_datetime(current_time, 3))
    add_investor('Jacob', 1000, 'strategy_2', adjusted_datetime(current_time, 2))
    add_investor('Gwyn', 1000, 'strategy_3', adjusted_datetime(current_time, 1))
    add_investor('Axel', 1000, 'strategy_4', adjusted_datetime(current_time, 0))
    st.sidebar.success('The game has been reset.')
    st.rerun()

# Investors Overview
st.sidebar.header('Investors Overview')
investors = get_investors()

st.sidebar.header('Select Investor')
investor_names = {investor[0]: investor[1] for investor in investors}

# if st.sidebar.button('Trading Day'):
#     st.session_state.trading_started = True
    #count = st_autorefresh(interval=5000, limit=10, key="investor_counter")
    #st.sidebar.write(f"Current count: {count + 1}")




selected_investor = select_current_investor()

st.session_state.selected_investor = selected_investor
funds, coins, strategy = get_investor_details(selected_investor)
investor_name = investor_names[selected_investor]

price_history = get_price_history()
df = pd.DataFrame(price_history, columns=['transaction', 'coin_price'])
strategy_function = get_strategy_function(strategy)
if strategy_function:
    instruction, proportion = strategy_function(df)
    volume, price, previous_price = get_coin_status()
    if instruction == 'buy':
        message = buy_coins(selected_investor, int(proportion * funds / price), price)
    elif instruction == 'sell':
        message = sell_coins(selected_investor, int(proportion * coins), price)
    else:
        log_price(price)
        funds, coins, _ = get_investor_details(selected_investor)
        update_investor(selected_investor, funds, coins)
        message = 'Hold: No action taken'
    st.session_state.success_message = message

# Display metrics
volume, price, previous_price = get_coin_status()
st.header('Tulip Coin ($TC) Overview')
col1, col2 = st.columns(2)
col1.metric("Coin Volume", volume)
price_change = price - previous_price
price_delta = f"${price_change:.2f}" if price_change >= 0 else f"-${abs(price_change):.2f}"
col2.metric("Current Price", f"${price:.2f}", price_delta)
funds, coins, strategy = get_investor_details(selected_investor)
st.header(f'Investor Overview: {investor_name}')
st.write()

col1, col2, col3 = st.columns(3)
col1.metric("Investor Funds", f"${funds:.2f}")
col2.metric("Investor Coins", coins)
col3.metric("Total Assets", f"${funds + coins * price:.2f}")

# if st.session_state.success_message:
#     if st.session_state.success_message == 'Hold: No action taken':
#         st.info(st.session_state.success_message)
#     else:
#         st.success(st.session_state.success_message)
#     st.session_state.success_message = ""

st.divider()

for investor_id, investor_name in investors:
    funds, coins = get_investor_details(investor_id)[:2]
    total_assets = funds + coins * price
    st.sidebar.write(f'{investor_name}: ${total_assets:.2f}')

# Coin Price History Plot
price_history = get_price_history()
if price_history:
    df = pd.DataFrame(price_history, columns=['transaction', 'coin_price'])
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
    
    st.altair_chart(chart)

st.write('---')
st.write('Note: Coin price is adjusted based on the transaction volume relative to available coins.')

# Specify the timezone
timezone = pytz.timezone('Australia/Sydney')

# Get the current time in the specified timezone
current_datetime = datetime.now(timezone)

# Define the end time for 12:00 AM in the same timezone
end_datetime = datetime(2024, 7, 19)

# Check if the current time is before the end time
#if current_datetime > end_datetime:
time.sleep(5)
st.rerun()