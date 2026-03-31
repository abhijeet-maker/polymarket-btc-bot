"""Multi-signal volatility-normalized probability model"""

from collections import deque
from math import exp
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProbabilityModel:
    """
    Volatility-normalized 4-signal model for BTC up/down prediction.
    
    Signals:
    1. Distance: (current_price - target) / vol (weight: 0.40)
    2. Short momentum: (price[-1] - price[-5]) / vol (weight: 0.25)
    3. Medium momentum: (price[-1] - price[-15]) / vol (weight: 0.20)
    4. Acceleration: short_mom - (price[-5] - price[-10]) / vol (weight: 0.15)
    """
    
    def __init__(self, history_size: int = 60):
        self.prices = deque(maxlen=history_size)
        self.min_prices_required = 20
        self.vol_floor = 0.5
        self.sigmoid_scale = 0.5
    
    def add_price(self, price: float) -> None:
        """Add new price to history"""
        self.prices.append(price)
    
    def compute_probability(self, target_price: float) -> float:
        """
        Estimate P(BTC > target at round end).
        Returns 0.5 if insufficient data.
        """
        if len(self.prices) < self.min_prices_required:
            return 0.5
        
        prices = list(self.prices)
        current = prices[-1]
        
        # 1. Compute volatility
        vol = self._compute_volatility(prices)
        
        # 2. Compute signals (normalized by vol)
        distance = (current - target_price) / vol
        short_mom = (prices[-1] - prices[-5]) / vol if len(prices) >= 5 else 0
        medium_mom = (prices[-1] - prices[-15]) / vol if len(prices) >= 15 else 0
        accel = self._compute_acceleration(prices, vol)
        
        # 3. Weighted combination
        score = (
            0.40 * distance +
            0.25 * short_mom +
            0.20 * medium_mom +
            0.15 * accel
        )
        
        # 4. Sigmoid squash
        prob = 1.0 / (1.0 + exp(-score * self.sigmoid_scale))
        
        # 5. Confidence adjustment (shrink in high vol)
        confidence = min(1.0, 1.0 / (1.0 + vol / 10.0))
        prob = 0.5 + (prob - 0.5) * confidence
        
        # 6. Clamp to [0.05, 0.95]
        prob = max(0.05, min(0.95, prob))
        
        return prob
    
    def _compute_volatility(self, prices: list) -> float:
        """Compute std dev of recent returns"""
        returns = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        vol = variance ** 0.5
        return max(self.vol_floor, vol)
    
    def _compute_acceleration(self, prices: list, vol: float) -> float:
        """Compute acceleration (change in momentum)"""
        if len(prices) < 10:
            return (prices[-1] - prices[-5]) / vol if len(prices) >= 5 else 0
        
        short_mom = (prices[-1] - prices[-5]) / vol
        prev_mom = (prices[-5] - prices[-10]) / vol
        return short_mom - prev_mom
    
    def reset(self) -> None:
        """Clear price history"""
        self.prices.clear()