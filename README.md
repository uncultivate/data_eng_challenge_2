# Tulip Coin Trading App

Welcome to the Tulip Coin Trading App, where you can simulate trading in the exciting world of Tulip Coins! This app allows you to create investors, execute trades, and visualize the coin price history using various trading strategies.

## Tulipmania
Step right up and plant the seeds of your success with Tulip Coin! Who wouldn't want to invest in the next big thing that combines the rich history of 17th-century Holland with the endless hype of the digital age? With its limited supply and radiant hues, Tulip Coin is your ticket to a blooming fortune! Join the garden of savvy investors who see the potential in this floral commodity on a rocket to the moon! 🌷💰

## Features

- **Investors Management**: Add, view, and manage multiple investors with different strategies.
- **Trading Simulation**: Buy and sell coins based on predefined strategies.
- **Coin Price Tracking**: Monitor and log the price history of Tulip Coins.
- **Visualizations**: View real-time price history plots.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/tulip-coin-trading-app.git
    cd tulip-coin-trading-app
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the Streamlit app:
    ```sh
    streamlit run app.py
    ```

## App Structure

### Database Initialization
The database consists of three tables:
- `price_history`: Records the timestamp and price of Tulip Coins.
- `investors`: Stores investor information including name, funds, coins, and strategy.
- `coin_status`: Tracks the current volume, price, and previous price of Tulip Coins.

### Trading Logic
- **Buying and Selling**: Investors can buy and sell coins based on their available funds and the current price.
- **Strategies**: Implement different strategies to decide when to buy or sell coins.
  - `strategy_1`: Buys more coins initially, then adjusts based on price history.
  - `strategy_2`: Buys or sells based on price changes.
  - `strategy_3`: Buys at the lowest price and sells at the highest price in recent history.
  - `strategy_4`: Buys after a certain number of transactions.

### User Interface
- **Investors Overview**: Sidebar displays the list of investors and their total assets.
- **Trading Actions**: Automatically executes trades based on the selected strategy.
- **Price History Plot**: Displays the historical price data using Altair charts.

## Usage

1. **Add Investors**: Add new investors with specific funds and strategies.
2. **View Investor Details**: View the funds, coins, and strategy of selected investors.
3. **Execute Trades**: Automatically execute buy/sell actions based on predefined strategies.
4. **Reset Game**: Reset the simulation to start fresh.

## Example

```python
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
