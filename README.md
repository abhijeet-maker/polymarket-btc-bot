# Polymarket BTC Trading Bot

An automated trading bot designed for Polymarket's BTC 5-minute markets. It streams real-time Bitcoin prices via Binance WebSockets, computes probabilities using a mathematical model, and automatically calculates edge to place trades on Polymarket's CLOB (Central Limit Order Book).

## 🚀 Getting Started

### Prerequisites

- Windows OS
- Python 3.8 to 3.11 installed and added to your systemic `PATH`
- A Polygon wallet with USDC for live trading and MATIC to cover network gas fees (though Polymarket's relayer often subsidizes gas)

### 1. Installation

Run the automated setup script to install all necessary dependencies and scaffold the project:

```cmd
setup.bat
```

This will automatically:
- Check for Python
- Set up an isolated clean Virtual Environment (`.venv`)
- Install all essential libraries from `requirements.txt`
- Generate an initial `.env` file for you from the template

### 2. Configuration

Open the newly created `.env` file in your preferred text editor (like VS Code or Notepad). You must edit it to ensure the bot can securely interact with Polymarket. 

**Required Environment Variables:**
- `PRIVATE_KEY`: Your wallet's private key (Starts with `0x...` or similar). **Never share this key with anyone!**

**Optional Tunable Parameters:**
- `BANKROLL`: (Default `50.0`) The total bankroll size in USDC the bot considers available.
- `EDGE_THRESHOLD`: (Default `0.18` / 18%) The minimal expected edge required to enter a position.
- `HOLD_THRESHOLD`: (Default `0.10` / 10%) The minimum edge required to keep an open position. It will automatically exit if the edge drips below this threshold.
- `MAX_BET_FRACTION`: (Default `0.12` / 12%) The maximum portion of the bankroll to wager on a single trade.
- `EXIT_BUFFER_S`: (Default `15`) The minimum seconds remaining in the market required before the bot halts trading out of caution.

### 3. Usage

The project splits execution into two clear paths: a sandbox for mathematical/strategy verification and a live trading engine.

#### Developer / Simulation Mode
Run this mode to observe the bot's behavior without executing true financial transactions. Highly recommended for first-time use.
```cmd
run_dev.bat
```

#### Live Trading Mode
**⚠️ WARNING: THIS WILL EXECUTE TRADES WITH REAL USDC.** 
Once confident in the strategy and setup, initiate live operations by running:
```cmd
run_live.bat
```

## 📁 Project Structure

- `src/` - Primary source code
  - `bot.py`: The Main Orchestrator integrating all modular components.
  - `feeds/`: Data ingestion (Binance WebSockets, Polymarket CLOB Polling)
  - `market/`: State models defining Market and Position structures.
  - `probability/`: Core mathematical calculations to compute implied odds from price histories.
  - `trading/`: Strategy execution logic and order routing.
  - `utils/`: Reusable helpers encompassing standardized logging modules.
- `tests/` - Unit and integration testing suite.
- `setup.bat`, `run_dev.bat`, `run_live.bat`: Windows batch execution helpers.
