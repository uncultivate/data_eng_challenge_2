Tulip Coin Trading App
Welcome to the Tulip Coin Trading App, where you can simulate trading in the exciting world of Tulip Coins! This app allows you to create investors, execute trades, and visualize the coin price history using various trading strategies.

Features
Investors Management: Add, view, and manage multiple investors with different strategies.
Trading Simulation: Buy and sell coins based on predefined strategies.
Coin Price Tracking: Monitor and log the price history of Tulip Coins.
Visualizations: View real-time price history plots.
Installation
Clone the repository:

sh
Copy code
git clone https://github.com/yourusername/tulip-coin-trading-app.git
cd tulip-coin-trading-app
Install the required packages:

sh
Copy code
pip install -r requirements.txt
Run the Streamlit app:

sh
Copy code
streamlit run app.py
App Structure
Database Initialization
The database consists of three tables:

price_history: Records the timestamp and price of Tulip Coins.
investors: Stores investor information including name, funds, coins, and strategy.
coin_status: Tracks the current volume, price, and previous price of Tulip Coins.
Trading Logic
Buying and Selling: Investors can buy and sell coins based on their available funds and the current price.
Strategies: Implement different strategies to decide when to buy or sell coins.
strategy_1: Buys more coins initially, then adjusts based on price history.
strategy_2: Buys or sells based on price changes.
strategy_3: Buys at the lowest price and sells at the highest price in recent history.
strategy_4: Buys after a certain number of transactions.
User Interface
Investors Overview: Sidebar displays the list of investors and their total assets.
Trading Actions: Automatically executes trades based on the selected strategy.
Price History Plot: Displays the historical price data using Altair charts.
Usage
Add Investors: Add new investors with specific funds and strategies.
View Investor Details: View the funds, coins, and strategy of selected investors.
Execute Trades: Automatically execute buy/sell actions based on predefined strategies.
Reset Game: Reset the simulation to start fresh.
Example
python
Copy code
# Adding a new investor
add_investor('Alice', 10000, 'strategy_1')

# Viewing investors
investors = get_investors()
print(investors)

# Execute a buy action
message = buy_coins(investor_id=1, num_coins=100, current_price=0.2)
print(message)

# Execute a sell action
message = sell_coins(investor_id=1, num_coins=50, current_price=0.25)
print(message)
License
This project is licensed under the MIT License.

Acknowledgements
Special thanks to the contributors and the open-source community for their valuable resources and support.

Contact
For any inquiries, please contact your_email@example.com.

Step right up and plant the seeds of your success with Tulip Coin! Who wouldn't want to invest in the next big thing that combines the rich history of 17th-century Holland with the endless hype of the digital age? With its limited supply and radiant hues, Tulip Coin is your ticket to a blooming fortune! Join the garden of savvy investors who see the potential in this floral commodity on a rocket to the moon! 🌷💰

Happy trading!

Reset Instructions
To reset the game, use the Reset button in the sidebar. This will drop all tables and reinitialize the database with default investors and settings.

python
Copy code
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
End Time Configuration
To set an end time for the trading day, use the sidebar input to specify the finish time in the format HH:MM.

python
Copy code
finish_time = st.sidebar.text_input("End time")

if finish_time:
    # Specify the timezone
    timezone = pytz.timezone('Australia/Sydney')
    # Get the current time
    now = datetime.now(timezone)
    current_time = now.time()
    # Define the time to compare (example: 3:30 PM)
    end_time = datetime.strptime(finish_time, '%H:%M').time()
    # Check if compare_time is earlier than the current time
    if end_time > current_time:
        time.sleep(5)
        st.rerun()
Enjoy simulating your trading strategies and see how your investments grow with Tulip Coin!
