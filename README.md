# MEXC Triangular Arbitrage Bot

This project is a Python-based bot that performs triangular arbitrage on the MEXC cryptocurrency exchange. It calculates potential arbitrage opportunities by comparing the price differences between three pairs and executes trades when profitable opportunities are found.

## Features

- Automatically fetches price data for specified pairs (e.g., BTC/USDT, ETH/USDT, ETH/BTC).
- Calculates potential profit for triangular arbitrage trades.
- Executes limit orders using the MEXC Spot API.
- Configurable via a graphical user interface (GUI) for easy setup.
- Built-in logging for real-time monitoring of arbitrage activities.

## Requirements

- Python 3.x
- Required Python packages:
  - `requests`
  - `hashlib`
  - `hmac`
  - `logging`
  - `tkinter`
  - `mexc_sdk` (MEXC Spot API wrapper)

