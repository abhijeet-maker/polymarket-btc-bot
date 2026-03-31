"""CLOB API polling"""

import threading
import time
from typing import Optional

from src.config import BotConfig
from src.market.discovery import find_active_market
from src.market.models import Market
from src.market.pricing import fetch_order_book
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ClobPoller:
    """Background thread for market discovery and price polling"""
    
    def __init__(self, config: BotConfig, on_market_update_callback):
        self.config = config
        self.on_market_update_callback = on_market_update_callback
        self.running = False
        self.thread = None
        self.last_poll = 0
    
    def start(self) -> None:
        """Start background polling thread"""
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()
        logger.info("CLOB poller started")
    
    def stop(self) -> None:
        """Stop background polling thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("CLOB poller stopped")
    
    def _poll_loop(self) -> None:
        """Main polling loop"""
        while self.running:
            try:
                current_time = int(time.time())
                if current_time - self.last_poll >= self.config.clob_poll_s:
                    self.last_poll = current_time
                    self._poll_once()
                
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Poll loop error: {e}")
                time.sleep(1)
    
    def _poll_once(self) -> None:
        """Single poll cycle: discover market and fetch prices"""
        try:
            market = find_active_market(self.config)
            if market:
                yes_mid, _ = fetch_order_book(market.tokens["yes"], self.config)
                no_mid, _ = fetch_order_book(market.tokens["no"], self.config)
                
                market.yes_mid = yes_mid
                market.no_mid = no_mid
                
                self.on_market_update_callback(market)
        except Exception as e:
            logger.debug(f"Poll cycle error: {e}")