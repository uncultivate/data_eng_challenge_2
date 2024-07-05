import streamlit as st
import sqlite3
import datetime
import altair as alt
import pandas as pd

# Initialize SQLite database
conn = sqlite3.connect('coin_price_history.db')
c = conn.cursor()

# Create tables
c.execute('''
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        coin_price REAL
    )
''')

# Create or update the investors table schema
c.execute('''
    CREATE TABLE IF NOT EXISTS investors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        funds REAL,
        coins INTEGER,
        strategy TEXT
    )
''')
conn.commit()

def log_price(price):
    timestamp = datetime.datetime.now().isoformat()
    c.execute('INSERT INTO price_history (timestamp, coin_price) VALUES (?, ?)', (timestamp, price))
    conn.commit()

# Initial settings
coin_volume = 40000
initial_coin_price = 1.0

# Session state to store dynamic variables
if 'coin_volume' not in st.session_state:
    st.session_state.coin_volume = coin_volume
if 'coin_price' not in st.session_state:
    st.session_state.coin_price = initial_coin_price
    log_price(initial_coin_price)  # Log initial share price
if 'selected_investor' not in st.session_state:
    st.session_state.selected_investor = None
if 'current_investor_index' not in st.session_state:
    st.session_state.current_investor_index = 0

# Function to add a new investor
def add_investor(name, funds, strategy):
    c.execute('INSERT INTO investors (name, funds, coins, strategy) VALUES (?, ?, 1000, ?)', (name, funds, strategy))
    conn.commit()

# Function to get list of investors
def get_investors():
    c.execute('SELECT id, name FROM investors')
    return c.fetchall()

# Function to get investor details
def get_investor_details(investor_id):
    c.execute('SELECT funds, coins FROM investors WHERE id = ?', (investor_id,))
    return c.fetchone()

# Function to update investor details
def update_investor(investor_id, funds, coins):
    c.execute('UPDATE investors SET funds = ?, coins = ? WHERE id = ?', (funds, coins, investor_id))
    conn.commit()

# Functions to handle buying and selling of coins
def buy_coins(investor_id, num_coins):
    funds, coins, _ = get_investor_details(investor_id)
    total_cost = num_coins * st.session_state.coin_price
    if total_cost <= funds and num_coins <= st.session_state.coin_volume:
        funds -= total_cost
        coins += num_coins
        st.session_state.coin_volume -= num_coins
        st.session_state.coin_price *= (1 + num_coins / st.session_state.coin_volume * 5)
        update_investor(investor_id, funds, coins)
        log_price(st.session_state.coin_price)  # Log updated share price
        st.success(f'Bought {num_coins} coins at ${st.session_state.coin_price:.2f} each')

def sell_coins(investor_id, num_coins):
    funds, coins, _ = get_investor_details(investor_id)  # Ignore the strategy value
    if num_coins <= coins:
        total_revenue = num_coins * st.session_state.coin_price
        funds += total_revenue
        coins -= num_coins
        st.session_state.coin_volume += num_coins
        st.session_state.coin_price *= (1 - num_coins / st.session_state.coin_volume * 5)
        update_investor(investor_id, funds, coins)
        log_price(st.session_state.coin_price)  # Log updated share price
        st.success(f'Sold {num_coins} coins at ${st.session_state.coin_price:.2f} each')


def get_price_history():
    c.execute('SELECT id, coin_price FROM price_history')
    return c.fetchall()

st.title('Challenge #2: Trading Day')

#################################################
# INVESTORS

price_history = get_price_history()
if price_history:
    df = pd.DataFrame(price_history, columns=['transaction', 'coin_price'])

def strategy_1(df: pd.DataFrame) -> (str, float):
    if len(df) < 2:
        return 'buy', 0.2 
        
    last_price = df['coin_price'].iloc[-1]
    second_last_price = df['coin_price'].iloc[-2]
    
    if last_price > second_last_price:
        return 'sell', 0.5
    else:
        return 'buy', 0.4

    
def strategy_2(df: pd.DataFrame) -> (str, float):
    if len(df) < 2:
        return 'sell', 0.5  # Not enough data to make a decision

    last_price = df['coin_price'].iloc[-1]
    second_last_price = df['coin_price'].iloc[-2]
    price_change = (last_price - second_last_price) / second_last_price
    if price_change > 0.02:
        return 'sell', 0.5
    elif price_change < 0:
        return 'buy', 0.5
    else:
        return 'hold', 0.0

def strategy_3(df: pd.DataFrame) -> (str, float):
    if len(df) < 5:
        return 'buy', 0.1  # Not enough data to make a decision

    last_price = df['coin_price'].iloc[-1]
    last_five_prices = df['coin_price'].iloc[-5:]

    if last_price == last_five_prices.max():
        return 'sell', 0.5
    elif last_price == last_five_prices.min():
        return 'buy', 0.5
    else:
        return 'hold', 0.0

# Add new investor
st.sidebar.header('Add New Investor')
new_investor_name = st.sidebar.text_input('Investor Name')
new_investor_funds = st.sidebar.number_input('Initial Funds', min_value=1.0, value=1000.0)
strategy_options = ['strategy_1', 'strategy_2', 'strategy_3']
new_investor_strategy = st.sidebar.selectbox('Strategy', strategy_options)
if st.sidebar.button('Add Investor'):
    add_investor(new_investor_name, new_investor_funds, new_investor_strategy)
    st.sidebar.success(f'Investor {new_investor_name} added with strategy {new_investor_strategy}.')

# Sidebar button to reset investors table
if st.sidebar.button('Reset'):
    c.execute('DROP TABLE IF EXISTS investors')
    c.execute('''
        CREATE TABLE investors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            funds REAL,
            coins INTEGER,
            strategy TEXT
        )
    ''')
    c.execute('DROP TABLE IF EXISTS price_history')
    c.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            coin_price REAL
        )
    ''')
    conn.commit()
    st.sidebar.success('The game has been reset.')
    st.rerun()  # Rerun the app to update the state

# List of investors and their total assets in the sidebar
st.sidebar.header('Investors Overview')
investors = get_investors()
for investor_id, investor_name in investors:
    funds, coins = get_investor_details(investor_id)[:2]
    total_assets = funds + coins * st.session_state.coin_price
    st.sidebar.write(f'{investor_name}: ${total_assets:.2f}')

# Select investor
st.sidebar.header('Select Investor')
investor_names = {investor[0]: investor[1] for investor in investors}
selected_investor_id = st.sidebar.selectbox('Investor', list(investor_names.keys()), format_func=lambda x: investor_names[x])

# Function to get the strategy function by name
def get_strategy_function(strategy_name):
    strategies = {
        'strategy_1': strategy_1,
        'strategy_2': strategy_2,
        'strategy_3': strategy_3
    }
    return strategies.get(strategy_name)

# Function to get investor details, including the strategy
def get_investor_details(investor_id):
    c.execute('SELECT funds, coins, strategy FROM investors WHERE id = ?', (investor_id,))
    return c.fetchone()

# Integration into the Streamlit App
if selected_investor_id:
    st.session_state.selected_investor = selected_investor_id
    funds, coins, strategy = get_investor_details(selected_investor_id)
    investor_name = investor_names[selected_investor_id]

    st.header('CensusCoin (CC) Overview')  
    col1, col2 = st.columns(2)
    col1.metric("Coin Volume", st.session_state.coin_volume)
    col2.metric("Current Price", f"${st.session_state.coin_price:.2f}")

    st.header(f'Investor Overview: {investor_name}')
    col1, col2, col3 = st.columns(3)
    col1.metric("Investor Funds", f"${funds:.2f}")
    col2.metric("Investor coins", coins)
    col3.metric("Total Assets", f"${funds + coins * st.session_state.coin_price:.2f}")
 
    if st.button('Execute Trade'):
        price_history = get_price_history()
        df = pd.DataFrame(price_history, columns=['transaction', 'coin_price'])
        strategy_function = get_strategy_function(strategy)
        if strategy_function:
            instruction, proportion = strategy_function(df)
            if instruction == 'buy':
                num_coins_to_buy = int((proportion * funds) / st.session_state.coin_price)
                if num_coins_to_buy > 0:
                    buy_coins(selected_investor_id, num_coins_to_buy)
                    st.rerun()  # Rerun the app to update metrics
            elif instruction == 'sell':
                num_coins_to_sell = int(proportion * coins)
                if num_coins_to_sell > 0:
                    sell_coins(selected_investor_id, num_coins_to_sell)
                    st.rerun()  # Rerun the app to update metrics
            else:
                st.info('Hold: No action taken')

        # Select the next investor
        st.session_state.current_investor_index = (st.session_state.current_investor_index + 1) % len(investor_names)
        st.rerun()
    st.divider()

    # st.subheader('Buy coins')
    # num_coins_to_buy = st.number_input('Number of coins to buy:', min_value=1, max_value=st.session_state.coin_volume, value=1)
    # if st.button('Buy'):
    #     buy_coins(selected_investor_id, num_coins_to_buy)
    #     st.rerun()  # Rerun the app to update metrics

    # st.subheader('Sell coins')
    # if coins > 0:
    #     num_coins_to_sell = st.number_input('Number of coins to sell:', min_value=1, max_value=coins, value=1)
    #     if st.button('Sell'):
    #         sell_coins(selected_investor_id, num_coins_to_sell)
    #         st.rerun()  # Rerun the app to update metrics
    # else:
    #     st.write("You don't have any coins to sell.")

# Retrieve and plot share price history
price_history = get_price_history()
if price_history:
    df = pd.DataFrame(price_history, columns=['transaction', 'coin_price'])
    
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('transaction:Q', title='Transactions'),
        y=alt.Y('coin_price:Q', title='Share Price', axis=alt.Axis(format='$'))
    ).properties(
        title='Share Price History',
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
st.write('Note: Share price is adjusted based on the transaction volume relative to available coins.')
