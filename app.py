import streamlit as st
import sqlite3
import datetime
import altair as alt
import pandas as pd

# Initialize SQLite database
conn = sqlite3.connect('share_price_history.db')
c = conn.cursor()

# Create tables
c.execute('''
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        share_price REAL
    )
''')

# Create or update the investors table schema
c.execute('''
    CREATE TABLE IF NOT EXISTS investors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        funds REAL,
        shares INTEGER,
        strategy TEXT
    )
''')
conn.commit()

def log_price(price):
    timestamp = datetime.datetime.now().isoformat()
    c.execute('INSERT INTO price_history (timestamp, share_price) VALUES (?, ?)', (timestamp, price))
    conn.commit()

# Initial settings
company_shares = 3000
initial_share_price = 1.0

# Session state to store dynamic variables
if 'company_shares' not in st.session_state:
    st.session_state.company_shares = company_shares
if 'share_price' not in st.session_state:
    st.session_state.share_price = initial_share_price
    log_price(initial_share_price)  # Log initial share price
if 'selected_investor' not in st.session_state:
    st.session_state.selected_investor = None
if 'current_investor_index' not in st.session_state:
    st.session_state.current_investor_index = 0

# Function to add a new investor
def add_investor(name, funds, strategy):
    c.execute('INSERT INTO investors (name, funds, shares, strategy) VALUES (?, ?, 100, ?)', (name, funds, strategy))
    conn.commit()

# Function to get list of investors
def get_investors():
    c.execute('SELECT id, name FROM investors')
    return c.fetchall()

# Function to get investor details
def get_investor_details(investor_id):
    c.execute('SELECT funds, shares FROM investors WHERE id = ?', (investor_id,))
    return c.fetchone()

# Function to update investor details
def update_investor(investor_id, funds, shares):
    c.execute('UPDATE investors SET funds = ?, shares = ? WHERE id = ?', (funds, shares, investor_id))
    conn.commit()

# Functions to handle buying and selling of shares
def buy_shares(investor_id, num_shares):
    funds, shares, _ = get_investor_details(investor_id)
    total_cost = num_shares * st.session_state.share_price
    if total_cost <= funds and num_shares <= st.session_state.company_shares:
        funds -= total_cost
        shares += num_shares
        st.session_state.company_shares -= num_shares
        st.session_state.share_price *= (1 + num_shares / st.session_state.company_shares)
        update_investor(investor_id, funds, shares)
        log_price(st.session_state.share_price)  # Log updated share price
        st.success(f'Bought {num_shares} shares at ${st.session_state.share_price:.2f} each')

def sell_shares(investor_id, num_shares):
    funds, shares, _ = get_investor_details(investor_id)  # Ignore the strategy value
    if num_shares <= shares:
        total_revenue = num_shares * st.session_state.share_price
        funds += total_revenue
        shares -= num_shares
        st.session_state.company_shares += num_shares
        st.session_state.share_price *= (1 - num_shares / st.session_state.company_shares)
        update_investor(investor_id, funds, shares)
        log_price(st.session_state.share_price)  # Log updated share price
        st.success(f'Sold {num_shares} shares at ${st.session_state.share_price:.2f} each')


def get_price_history():
    c.execute('SELECT id, share_price FROM price_history')
    return c.fetchall()

st.title('AI-BS Trading Day')

#################################################
# INVESTORS

price_history = get_price_history()
if price_history:
    df = pd.DataFrame(price_history, columns=['transaction', 'share_price'])

def strategy_1(df: pd.DataFrame) -> (str, float):
    if len(df) < 2:
        return 'buy', 0.2 
        
    last_price = df['share_price'].iloc[-1]
    second_last_price = df['share_price'].iloc[-2]
    
    if last_price > second_last_price:
        return 'sell', 0.5
    else:
        return 'buy', 0.4

    
def strategy_2(df: pd.DataFrame) -> (str, float):
    if len(df) < 2:
        return 'sell', 0.5  # Not enough data to make a decision

    last_price = df['share_price'].iloc[-1]
    second_last_price = df['share_price'].iloc[-2]
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

    last_price = df['share_price'].iloc[-1]
    last_five_prices = df['share_price'].iloc[-5:]

    if last_price == last_five_prices.max():
        return 'sell', 0.5
    elif last_price == last_five_prices.min():
        return 'buy', 0.5
    else:
        return 'hold', 0.0

# Add new investor
st.sidebar.header('Add New Investor')
new_investor_name = st.sidebar.text_input('Investor Name')
new_investor_funds = st.sidebar.number_input('Initial Funds', min_value=1.0, value=100.0)
strategy_options = ['strategy_1', 'strategy_2', 'strategy_3']
new_investor_strategy = st.sidebar.selectbox('Strategy', strategy_options)
if st.sidebar.button('Add Investor'):
    add_investor(new_investor_name, new_investor_funds, new_investor_strategy)
    st.sidebar.success(f'Investor {new_investor_name} added with strategy {new_investor_strategy}.')


# Select investor
st.sidebar.header('Select Investor')
investors = get_investors()
investor_names = {investor[0]: investor[1] for investor in investors}
selected_investor_id = st.sidebar.selectbox('Investor', list(investor_names.keys()), format_func=lambda x: investor_names[x])

# Sidebar button to reset investors table
if st.sidebar.button('Reset'):
    c.execute('DROP TABLE IF EXISTS investors')
    c.execute('''
        CREATE TABLE investors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            funds REAL,
            shares INTEGER,
            strategy TEXT
        )
    ''')
    c.execute('DROP TABLE IF EXISTS price_history')

    c.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            share_price REAL
        )
    ''')
    conn.commit()
    st.sidebar.success('The game has been reset.')
    st.rerun()  # Rerun the app to update the state

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
    c.execute('SELECT funds, shares, strategy FROM investors WHERE id = ?', (investor_id,))
    return c.fetchone()

# Integration into the Streamlit App
if selected_investor_id:
    st.session_state.selected_investor = selected_investor_id
    funds, shares, strategy = get_investor_details(selected_investor_id)

    st.header('Company Overview')  
    col1, col2 = st.columns(2)
    col1.metric("Company Shares Available", st.session_state.company_shares)
    col2.metric("Current Share Price", f"${st.session_state.share_price:.2f}")

    st.header('Investor Overview')
    col1, col2, col3 = st.columns(3)
    col1.metric("Investor Funds", f"${funds:.2f}")
    col2.metric("Investor Shares", shares)
    col3.metric("Total Assets", f"${funds + shares * st.session_state.share_price:.2f}")

    

    st.subheader('Automatic Trading Instructions')
   
    if st.button('Execute Instruction'):
        price_history = get_price_history()
        df = pd.DataFrame(price_history, columns=['transaction', 'share_price'])
        strategy_function = get_strategy_function(strategy)
        if strategy_function:
            instruction, proportion = strategy_function(df)
            if instruction == 'buy':
                num_shares_to_buy = int((proportion * funds) / st.session_state.share_price)
                if num_shares_to_buy > 0:
                    buy_shares(selected_investor_id, num_shares_to_buy)
                    st.rerun()  # Rerun the app to update metrics
            elif instruction == 'sell':
                num_shares_to_sell = int(proportion * shares)
                if num_shares_to_sell > 0:
                    sell_shares(selected_investor_id, num_shares_to_sell)
                    st.rerun()  # Rerun the app to update metrics
            else:
                st.info('Hold: No action taken')

        # Select the next investor
        st.session_state.current_investor_index = (st.session_state.current_investor_index + 1) % len(investor_names)
        st.rerun()

    st.subheader('Buy Shares')
    num_shares_to_buy = st.number_input('Number of shares to buy:', min_value=1, max_value=st.session_state.company_shares, value=1)
    if st.button('Buy'):
        buy_shares(selected_investor_id, num_shares_to_buy)
        st.rerun()  # Rerun the app to update metrics

    st.subheader('Sell Shares')
    if shares > 0:
        num_shares_to_sell = st.number_input('Number of shares to sell:', min_value=1, max_value=shares, value=1)
        if st.button('Sell'):
            sell_shares(selected_investor_id, num_shares_to_sell)
            st.rerun()  # Rerun the app to update metrics
    else:
        st.write("You don't have any shares to sell.")

# Retrieve and plot share price history
price_history = get_price_history()
if price_history:
    df = pd.DataFrame(price_history, columns=['transaction', 'share_price'])
    
    chart = alt.Chart(df).mark_line(point=True).encode(
        x='transaction:Q',
        y='share_price:Q'
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
st.write('Note: Share price is adjusted based on the transaction volume relative to available shares.')
