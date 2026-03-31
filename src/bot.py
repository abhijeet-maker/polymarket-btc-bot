"""
Main bot orchestrator - coordinates all components
"""

import sys
import threading
import time
from collections import deque

from src.config import BotConfig, get_config
from src.feeds.binance import BinanceWsFeed
from src.feeds.clob import ClobPoller
from src.market.models import Market, Position
from src.probability.model import ProbabilityModel
from src.trading.logic import TradingEngine
from src.trading.orders import cancel_order, place_order
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PolymarketBot:
    """Main trading bot orchestrator"""
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.prob_model = ProbabilityModel(config.price_history)
        self.trading_engine = TradingEngine(config, self.prob_model)
        
        # State
        self.active_market = Market()
        self.lock = threading.Lock()
        
        # Feeds
        self.clob_poller = ClobPoller(config, self._on_market_update)
        self.binance_feed = BinanceWsFeed(config, self._on_price_tick)
    
    def _on_market_update(self, market: Market) -> None:
        """Callback from CLOB poller"""
        with self.lock:
            self.active_market = market
    
    def _on_price_tick(self, price: float) -> None:
        """Callback from Binance WebSocket"""
        self.prob_model.add_price(price)
        
        with self.lock:
            market = self.active_market
            if not market.is_valid:
                return
        
        current_time = int(time.time())
        self._execute_trading_logic(current_time, market, price)
        self._print_dashboard(price, market)
    
    def _execute_trading_logic(
        self,
        current_time: int,
        market: Market,
        btc_price: float
    ) -> None:
        """Main trading decision logic"""
        if len(self.prob_model.prices) < 20:
            return
        
        # Calculate probability and edge
        our_prob = self.prob_model.compute_probability(market.target_price)
        edge = self.trading_engine.compute_edge(
            our_prob,
            market.yes_mid,
            market.no_mid
        )
        time_left = market.round_end - current_time
        
        # Entry logic
        if self.trading_engine.should_enter(edge, time_left):
            size = self.trading_engine.position_size(edge.best_edge)
            if size > 0:
                token_id = market.tokens[edge.direction.lower()]
                entry_price = (
                    market.yes_mid
                    if edge.direction == "YES"
                    else market.no_mid
                )
                order_id = place_order(
                    token_id,
                    entry_price,
                    size,
                    "BUY",
                    self.config
                )
                self.trading_engine.enter_position(
                    edge.direction,
                    entry_price,
                    size,
                    current_time,
                    order_id
                )
        
        # Exit logic
        elif self.trading_engine.position.is_open:
            pos_edge = (
                our_prob - market.yes_mid
                if self.trading_engine.position.direction == "YES"
                else (1 - our_prob) - market.no_mid
            )
            should_exit, reason = self.trading_engine.should_exit(
                pos_edge,
                time_left,
                current_time
            )
            
            if should_exit:
                if self.trading_engine.position.order_id:
                    cancel_order(
                        self.trading_engine.position.order_id,
                        self.config
                    )
                
                token_id = market.tokens[
                    self.trading_engine.position.direction.lower()
                ]
                exit_price = (
                    market.yes_mid
                    if self.trading_engine.position.direction == "YES"
                    else market.no_mid
                )
                place_order(
                    token_id,
                    exit_price,
                    self.trading_engine.position.size,
                    "SELL",
                    self.config
                )
                logger.info(f"Exit reason: {reason}")
                self.trading_engine.exit_position()
    
    def _print_dashboard(self, btc_price: float, market: Market) -> None:
        """Print real-time trading dashboard"""
        if len(self.prob_model.prices) < 20:
            return
        
        our_prob = self.prob_model.compute_probability(market.target_price)
        edge = self.trading_engine.compute_edge(
            our_prob,
            market.yes_mid,
            market.no_mid
        )
        time_left = market.round_end - int(time.time())
        status = (
            f"{self.trading_engine.position.direction} "
            f"{self.trading_engine.position.size:.2f}"
            if self.trading_engine.position.is_open
            else "[flat]"
        )
        
        print(
            f"\rBTC {btc_price:>10,.0f} | Target {market.target_price:>10,.2f} | "
            f"YES {market.yes_mid:.3f} NO {market.no_mid:.3f} | "
            f"Model {our_prob:.3f} | BestEdge +{edge.best_edge:.3f} {edge.direction} | "
            f"{time_left:>3}s | Bal ${self.trading_engine.balance:.2f} | {status}",
            end="",
            flush=True,
        )
    
    def run(self) -> None:
        """Start bot"""
        logger.info("=" * 100)
        logger.info("Polymarket BTC 5-Minute Edge Trading Bot")
        logger.info(f"DRY_RUN: {self.config.dry_run}")
        logger.info(f"Bankroll: ${self.config.bankroll}")
        logger.info(f"Edge Threshold: {self.config.edge_threshold}")
        logger.info("=" * 100)
        
        # Start background poller
        self.clob_poller.start()
        
        # Start Binance feed (blocks)
        try:
            self.binance_feed.start()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            self.clob_poller.stop()
            sys.exit(0)


def main():
    """Entry point"""
    config = get_config()
    bot = PolymarketBot(config)
    bot.run()


if __name__ == "__main__":
    main()