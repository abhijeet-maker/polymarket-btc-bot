"""
Configuration management for the trading bot
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class BotConfig:
    """Bot configuration parameters"""
    
    # Trading Parameters
    bankroll: float = 50.0
    edge_threshold: float = 0.18
    hold_threshold: float = 0.10
    max_bet_fraction: float = 0.12
    round_seconds: int = 300
    exit_buffer_s: int = 15
    
    # Data Parameters
    price_history: int = 60
    clob_poll_s: int = 2
    
    # API Configuration
    gamma_host: str = "https://gamma-api.polymarket.com"
    clob_host: str = "https://clob.polymarket.com"
    binance_ws: str = "wss://stream.binance.com:9443/ws/btcusdt@aggTrade"
    chain_id: int = 137
    
    # Wallet
    private_key: str = os.environ.get("PRIVATE_KEY", "")
    
    # Mode
    dry_run: bool = True
    verbose: bool = True
    
    def __post_init__(self):
        """Validate configuration on initialization"""
        if not self.private_key and not self.dry_run:
            raise ValueError("PRIVATE_KEY env var required for live trading")
        
        if not (0 < self.edge_threshold < 1):
            raise ValueError("edge_threshold must be between 0 and 1")
        
        if not (0 < self.bankroll):
            raise ValueError("bankroll must be positive")


def get_config() -> BotConfig:
    """Load config from environment or defaults"""
    return BotConfig(
        bankroll=float(os.environ.get("BANKROLL", 50.0)),
        edge_threshold=float(os.environ.get("EDGE_THRESHOLD", 0.18)),
        hold_threshold=float(os.environ.get("HOLD_THRESHOLD", 0.10)),
        max_bet_fraction=float(os.environ.get("MAX_BET_FRACTION", 0.12)),
        exit_buffer_s=int(os.environ.get("EXIT_BUFFER_S", 15)),
        clob_poll_s=int(os.environ.get("CLOB_POLL_S", 2)),
        chain_id=int(os.environ.get("CHAIN_ID", 137)),
        dry_run=os.environ.get("DRY_RUN", "true").lower() == "true",
        verbose=os.environ.get("VERBOSE", "true").lower() == "true",
    )