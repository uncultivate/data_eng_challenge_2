import streamlit as st
import sqlite3
from datetime import datetime, timedelta, time as timed
import time
import pytz
import altair as alt
import pandas as pd

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
            strategy TEXT
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
finish_time = st.sidebar.text_input("End time")

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
def add_investor(name, funds, strategy):
    c.execute('INSERT INTO investors (name, funds, coins, strategy) VALUES (?, ?, 0, ?)', (name, funds, strategy))
    conn.commit()

# Function to get list of investors
def get_investors():
    c.execute('SELECT id, name, funds, coins FROM investors')
    return c.fetchall()



# Function to get investor details
def get_investor_details(investor_id):
    c.execute('SELECT funds, coins, strategy FROM investors WHERE id = ?', (investor_id,))
    return c.fetchone()

# Function to update investor details
def update_investor(investor_id, funds, coins):
    c.execute('UPDATE investors SET funds = ?, coins = ?WHERE id = ?', (funds, coins, investor_id))
    conn.commit()

# Function to select current investor
def select_current_investor():
    c.execute('SELECT id FROM investors ORDER BY RANDOM()')
    return c.fetchone()[0]

# Functions to handle buying and selling of coins
def buy_coins(investor_id, num_coins, current_price):
    funds, coins, _ = get_investor_details(investor_id)
    total_cost = num_coins * current_price
    if total_cost <= funds:
        funds -= total_cost
        coins += num_coins
        volume, price, previous_price = get_coin_status()
        volume -= num_coins
        new_price = k / max(volume, 1)  # y = k/x
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
        new_price = k / max(1, volume)  # y = k/x
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
    if len(df) < 20:
        return 'buy', 0.2
    last_price = df['coin_price'].iloc[-1]
    second_last_price = df['coin_price'].iloc[-2]
    price_change = (last_price - second_last_price) / second_last_price
    if price_change > 0.02:
        return 'sell', 0.5
    elif price_change < 0:
        return 'buy', 0.5
    return 'sell', 0.4

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

# Investors Overview
st.sidebar.header('Investors Overview')

selected_investor = select_current_investor()
investors = get_investors()

investor_names = {investor[0]: investor[1] for investor in investors}
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
st.divider()

volume, price, previous_price = get_coin_status()

col1, col2, col3 = st.columns([1, 6, 3])
col2.header('Tulip Coin ($TC)')
col1.image('icon.png')
price_change = price - previous_price
price_delta = f"${price_change:.2f}" if price_change >= 0 else f"-${abs(price_change):.2f}"
col3.metric("Current Price", f"${price:.2f}", price_delta, label_visibility='collapsed')
#st.sidebar.metric("Coin Volume", volume)
funds, coins, strategy = get_investor_details(selected_investor)
st.subheader(f'Investor Overview: {investor_name}')

col1, col2, col3 = st.columns(3)
col1.metric("Investor Funds", f"${funds:.2f}")
col2.metric("Investor Coins", coins)
col3.metric("Total Assets", f"${funds + coins * price:.2f}")
investors = get_investors()

df = pd.DataFrame(investors, columns=["ID", "Name", "funds", "coins"])
# Calculate the total assets
df['Total Assets'] = df['funds'] + df['coins'] * price
# Format the 'total' column as currency
df['Total Assets'] = df['Total Assets'].apply(lambda x: f"${x:.2f}")
df = df[['Name','Total Assets']]
st.sidebar.dataframe(df, hide_index=True)

if st.session_state.success_message:
    if st.session_state.success_message == 'Hold: No action taken':
        st.info(st.session_state.success_message)
    else:
        st.success(st.session_state.success_message)
    st.session_state.success_message = ""

st.divider()

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
    
    st.altair_chart(chart, use_container_width=True)

st.write('Note: Coin price is adjusted based on the transaction volume relative to available coins.')
st.write('---')

st.write("Step right up and plant the seeds of your success with Tulip Coin! Who wouldn't want to invest in the next big thing that combines the rich history of 17th century Holland with the endless hype of the digital age? With its limited supply and radiant hues, Tulip Coin is your ticket to a blooming fortune! Join the garden of savvy investors who see the potential in this floral commodity on a rocket to the moon! 🌷💰")

if st.sidebar.button('Reset'):
    c.execute('DROP TABLE IF EXISTS investors')
    c.execute('DROP TABLE IF EXISTS price_history')
    c.execute('DROP TABLE IF EXISTS coin_status')
    init_db()

    add_investor('Whale', 20000, 'strategy_1')
    add_investor('Orca', 20000, 'strategy_2')
    add_investor('Narwhal', 10000, 'strategy_1')
    add_investor('Jacob', 1000, 'strategy_2')
    add_investor('Gwyn', 1000, 'strategy_3')
    add_investor('Axel', 1000, 'strategy_4')
    st.sidebar.success('The game has been reset.')
    st.rerun()

# Specify the timezone
timezone = pytz.timezone('Australia/Sydney')

# Get the current time
now = datetime.now(timezone)
current_time = now.time()

# Define the time to compare (example: 3:30 PM)
end_time = datetime.strptime(finish_time, '%H:%M').time()

# Check if compare_time is earlier than the current time
if end_time > current_time:

    # Check if the current time is before the end time
    #if current_datetime > end_datetime:
    time.sleep(5)
    st.rerun()

