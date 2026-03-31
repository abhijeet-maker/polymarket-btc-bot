"""Tests for probability model"""

import pytest

from src.probability.model import ProbabilityModel


def test_probability_model_initialization():
    """Test model initialization"""
    model = ProbabilityModel(history_size=60)
    assert len(model.prices) == 0
    assert model.min_prices_required == 20


def test_probability_with_insufficient_data():
    """Test probability returns 0.5 with insufficient data"""
    model = ProbabilityModel()
    model.add_price(100.0)
    prob = model.compute_probability(99.0)
    assert prob == 0.5


def test_probability_with_sufficient_data():
    """Test probability with sufficient price history"""
    model = ProbabilityModel()
    # Add 30 prices
    for i in range(30):
        model.add_price(100.0 + i)
    
    prob = model.compute_probability(120.0)
    assert 0.05 <= prob <= 0.95
    assert prob != 0.5  # Should differ from default


def test_volatility_floor():
    """Test volatility is floored at 0.5"""
    model = ProbabilityModel()
    # Add identical prices (zero volatility)
    for i in range(25):
        model.add_price(100.0)
    
    prob = model.compute_probability(100.0)
    # Should still compute without division error
    assert 0.05 <= prob <= 0.95