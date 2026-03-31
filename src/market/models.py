"""Data models for market state"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Market:
    """Active market state"""
    slug: str = ""
    condition_id: str = ""
    tokens: Dict[str, str] = field(default_factory=dict)  # {"yes": id, "no": id}
    target_price: float = 0.0
    yes_mid: float = 0.0
    no_mid: float = 0.0
    round_end: int = 0
    
    @property
    def is_valid(self) -> bool:
        """Check if market has required data"""
        return bool(
            self.slug and
            self.condition_id and
            self.tokens and
            self.target_price > 0 and
            self.round_end > 0
        )


@dataclass
class Position:
    """Current trading position"""
    direction: str = ""  # "YES" or "NO"
    entry_price: float = 0.0
    size: float = 0.0
    order_id: Optional[str] = None
    entry_time: float = 0.0
    
    @property
    def is_open(self) -> bool:
        """Check if position is currently open"""
        return bool(self.direction)


@dataclass
class Edge:
    """Edge calculation result"""
    yes_edge: float = 0.0
    no_edge: float = 0.0
    best_edge: float = 0.0
    direction: str = ""  # "YES" or "NO"
    
    @property
    def is_tradeable(self, threshold: float) -> bool:
        """Check if edge exceeds threshold"""
        return self.best_edge >= threshold