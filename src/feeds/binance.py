"""Binance WebSocket feed"""

import json
import threading

import websocket

from src.config import BotConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BinanceWsFeed:
    """Binance aggregated trade WebSocket feed"""
    
    def __init__(self, config: BotConfig, on_price_callback):
        self.config = config
        self.on_price_callback = on_price_callback
        self.ws = None
        self.connected = False
    
    def start(self) -> None:
        """Start WebSocket connection"""
        self.ws = websocket.WebSocketApp(
            self.config.binance_ws,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open,
        )
        # Run in main thread (blocks)
        self.ws.run_forever()
    
    def _on_message(self, ws, message: str) -> None:
        """Handle incoming price tick"""
        try:
            data = json.loads(message)
            price = float(data.get("p", 0))
            if price > 0:
                self.on_price_callback(price)
        except Exception as e:
            logger.error(f"Binance message error: {e}")
    
    def _on_error(self, ws, error) -> None:
        """Handle WebSocket error"""
        logger.error(f"Binance WS error: {error}")
        self.connected = False
    
    def _on_close(self, ws, close_status_code, close_msg) -> None:
        """Handle WebSocket close"""
        logger.info(f"Binance connection closed: {close_msg}")
        self.connected = False
    
    def _on_open(self, ws) -> None:
        """Handle WebSocket open"""
        logger.info("Binance WebSocket connected")
        self.connected = True