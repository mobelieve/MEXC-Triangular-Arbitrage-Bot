import requests
import time
import hashlib
import hmac
import logging
import threading
from tkinter import Tk, Label, Entry, Button, Text, END
from mexc_sdk import Spot

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants for MEXC (MAKER_FEE and TAKER_FEE should be dynamically updated as needed)
MAKER_FEE = 0.0  # 0.1% example maker fee
TAKER_FEE = 0.1  # 0.1% example taker fee
MEXC_BASE_URL = 'https://api.mexc.com'

class MexcArbitrageBot:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.client = Spot(api_key=api_key, api_secret=secret_key)
        self.bot_running = False

    # Function to create a signature for MEXC
    def create_mexc_signature(self, params):
        query_string = '&'.join([f"{key}={params[key]}" for key in sorted(params)])
        return hmac.new(self.secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    # Function to get account info from MEXC
    def get_mexc_account_info(self):
        try:
            endpoint = '/api/v3/account'
            timestamp = int(time.time() * 1000)
            params = {'timestamp': timestamp}
            params['signature'] = self.create_mexc_signature(params)
            headers = {'X-MEXC-APIKEY': self.api_key}
            url = MEXC_BASE_URL + endpoint
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raises an error for bad status codes
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching account info: {e}")
            return None

    # Function to get price from MEXC
    def get_mexc_price(self, symbol):
        try:
            url = f"{MEXC_BASE_URL}/api/v3/ticker/price"
            params = {'symbol': symbol}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return float(response.json()['price'])
        except Exception as e:
            logging.error(f"Error fetching price for {symbol}: {e}")
            return None

    # Function to place a limit order
    def place_limit_order(self, symbol, side, quantity, price):
        try:
            order = self.client.new_order(
                symbol=symbol,
                side=side,
                order_type='LIMIT',
                options={'quantity': quantity, 'price': price, 'timeInForce': 'GTC'}
            )
            logging.info(f"Order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Error placing limit order: {e}")
            return None

    # Function to execute triangular arbitrage
    def execute_triangular_arbitrage(self):
        btc_usdt_price = self.get_mexc_price('BTCUSDT')
        eth_usdt_price = self.get_mexc_price('ETHUSDT')
        eth_btc_price = self.get_mexc_price('ETHBTC')

        if btc_usdt_price and eth_usdt_price and eth_btc_price:
            initial_usd = 1500  # Example initial amount in USD
            btc_amount = initial_usd / btc_usdt_price
            eth_amount = btc_amount / eth_btc_price
            final_usd = eth_amount * eth_usdt_price

            maker_fee_amount = initial_usd * (MAKER_FEE / 100)
            taker_fee_amount = final_usd * (TAKER_FEE / 100)
            net_profit = final_usd - initial_usd - maker_fee_amount - taker_fee_amount

            logging.info(f"Initial USD: {initial_usd}, Final USD: {final_usd}, Net Profit: {net_profit}")

            if net_profit > 0:
                logging.info("Arbitrage opportunity found! Executing trades...")
                # Execute trades with limit orders
                self.place_limit_order('BTCUSDT', 'BUY', btc_amount, btc_usdt_price)
                self.place_limit_order('ETHBTC', 'BUY', eth_amount, eth_btc_price)
                self.place_limit_order('ETHUSDT', 'SELL', eth_amount, eth_usdt_price)
            else:
                logging.info("No arbitrage opportunity found.")
        else:
            logging.error("Failed to fetch prices for one or more trading pairs.")

    # Function to start the arbitrage bot
    def start(self):
        self.bot_running = True
        while self.bot_running:
            self.execute_triangular_arbitrage()
            time.sleep(10)

    # Function to stop the arbitrage bot
    def stop(self):
        self.bot_running = False

# GUI class
class ArbitrageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MEXC Triangular Arbitrage Bot")

        self.api_key_label = Label(root, text="API Key")
        self.api_key_label.pack()
        self.api_key_entry = Entry(root, width=50)
        self.api_key_entry.pack()

        self.secret_key_label = Label(root, text="Secret Key")
        self.secret_key_label.pack()
        self.secret_key_entry = Entry(root, width=50, show="*")
        self.secret_key_entry.pack()

        self.log_area = Text(root, width=80, height=20)
        self.log_area.pack()

        self.start_button = Button(root, text="Start Bot", command=self.start_bot)
        self.start_button.pack()

        self.stop_button = Button(root, text="Stop Bot", command=self.stop_bot)
        self.stop_button.pack()

        self.bot = None

    def start_bot(self):
        api_key = self.api_key_entry.get()
        secret_key = self.secret_key_entry.get()

        if not api_key or not secret_key:
            self.log("API Key and Secret Key are required.")
            return

        self.bot = MexcArbitrageBot(api_key, secret_key)
        self.log("Starting the arbitrage bot...")

        # Start the bot in a separate thread to keep the GUI responsive
        threading.Thread(target=self.bot.start, daemon=True).start()

    def stop_bot(self):
        if self.bot:
            self.bot.stop()
            self.log("Bot stopped.")

    def log(self, message):
        self.log_area.insert(END, f"{message}\n")
        self.log_area.see(END)

if __name__ == "__main__":
    root = Tk()
    gui = ArbitrageGUI(root)
    root.mainloop()
