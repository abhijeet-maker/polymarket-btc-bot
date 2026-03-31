"""Core trading decision logic"""

import time
from typing import Optional, Tuple

from src.config import BotConfig
from src.market.models import Edge, Market, Position
from src.probability.model import ProbabilityModel
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TradingEngine:
    """Manages entry/exit decisions and position tracking"""
    
    def __init__(self, config: BotConfig, prob_model: ProbabilityModel):
        self.config = config
        self.model = prob_model
        self.position = Position()
        self.balance = config.bankroll
    
    def compute_edge(
        self,
        our_prob: float,
        yes_mid: float,
        no_mid: float
    ) -> Edge:
        """
        Compute edge for YES and NO outcomes.
        Returns Edge with best_edge and direction.
        """
        yes_edge = our_prob - yes_mid
        no_edge = (1.0 - our_prob) - no_mid
        
        if yes_edge >= no_edge:
            best_edge = yes_edge
            direction = "YES"
        else:
            best_edge = no_edge
            direction = "NO"
        
        return Edge(
            yes_edge=yes_edge,
            no_edge=no_edge,
            best_edge=best_edge,
            direction=direction
        )
    
    def should_enter(
        self,
        edge: Edge,
        time_left: int
    ) -> bool:
        """Check if all entry conditions are met"""
        min_time = self.config.exit_buffer_s + 30
        return (
            not self.position.is_open and
            edge.best_edge >= self.config.edge_threshold and
            time_left > min_time
        )
    
    def should_exit(
        self,
        current_edge: float,
        time_left: int,
        current_time: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if any exit condition is triggered.
        Returns (should_exit, reason)
        """
        if not self.position.is_open:
            return False, None
        
        time_held = current_time - self.position.entry_time
        
        if current_edge < self.config.hold_threshold:
            return True, f"edge collapsed ({current_edge:.3f})"
        
        if time_left < self.config.exit_buffer_s:
            return True, f"round ending ({time_left}s)"
        
        if time_held > 240:
            return True, "max hold time (240s)"
        
        return False, None
    
    def position_size(self, edge: float) -> float:
        """
        Half-Kelly criterion with max bet fraction.
        size = (edge / 2) * bankroll, capped at MAX_BET_FRACTION * bankroll
        """
        kelly_size = (edge / 2.0) * self.balance
        max_size = self.config.max_bet_fraction * self.balance
        return min(kelly_size, max_size)
    
    def enter_position(
        self,
        direction: str,
        entry_price: float,
        size: float,
        current_time: int
    ) -> None:
        """Record position entry"""
        self.position = Position(
            direction=direction,
            entry_price=entry_price,
            size=size,
            entry_time=current_time
        )
        logger.info(
            f"[ENTRY] {direction} {size:.2f} @ {entry_price:.3f}"
        )
    
    def exit_position(self) -> None:
        """Clear position record"""
        if self.position.is_open:
            logger.info(
                f"[EXIT] {self.position.direction} "
                f"{self.position.size:.2f}"
            )
        self.position = Position()
    
    def update_balance(self, amount: float) -> None:
        """Update account balance"""
        self.balance += amount
        logger.debug(f"Balance updated: ${self.balance:.2f}")