"""Market discovery logic"""

import re
import time
from typing import Optional, Tuple

import requests

from src.config import BotConfig
from src.market.models import Market
from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_round_boundaries() -> Tuple[int, int, int]:
    """
    Get UTC epoch-aligned 300s round boundaries.
    Returns (base, next_boundary, prev_boundary)
    """
    now = int(time.time())
    base = now - (now % 300)
    return base, base + 300, base - 300


def find_active_market(config: BotConfig) -> Optional[Market]:
    """
    Discover active BTC 5-minute market.
    Returns Market object if found, else None.
    """
    base, next_boundary, prev_boundary = get_round_boundaries()
    candidates = [next_boundary, base, prev_boundary]

    for boundary in candidates:
        slug = f"btc-updown-5m-{boundary}"
        try:
            market = _fetch_market_from_gamma(slug, boundary, config)
            if market:
                return market
        except Exception as e:
            logger.debug(f"Error fetching {slug}: {e}")

    return None


def _fetch_market_from_gamma(
    slug: str,
    round_end: int,
    config: BotConfig
) -> Optional[Market]:
    """Fetch market details from Gamma API"""
    try:
        resp = requests.get(
            f"{config.gamma_host}/markets/slug/{slug}",
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            if "id" in data and "question" in data:
                condition_id = data["id"]
                target = extract_btc_target(
                    data.get("question", ""),
                    data.get("description", "")
                )
                if target:
                    market = _fetch_tokens_from_clob(
                        condition_id,
                        slug,
                        target,
                        round_end,
                        config
                    )
                    if market:
                        return market
    except Exception as e:
        logger.debug(f"Gamma API error: {e}")

    return None


def _fetch_tokens_from_clob(
    condition_id: str,
    slug: str,
    target: float,
    round_end: int,
    config: BotConfig
) -> Optional[Market]:
    """Fetch token IDs from CLOB API"""
    try:
        resp = requests.get(
            f"{config.clob_host}/markets/{condition_id}",
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            tokens = {}

            for token_info in data.get("tokens", []):
                outcome = token_info.get("outcome", "").upper()
                if outcome in ["UP", "YES", "HIGHER"]:
                    tokens["yes"] = token_info.get("token_id", "")
                elif outcome in ["DOWN", "NO", "LOWER"]:
                    tokens["no"] = token_info.get("token_id", "")

            if "yes" in tokens and "no" in tokens:
                market = Market(
                    slug=slug,
                    condition_id=condition_id,
                    tokens=tokens,
                    target_price=target,
                    round_end=round_end,
                )
                logger.info(f"Discovered market: {slug} (target: ${target:.2f})")
                return market
    except Exception as e:
        logger.debug(f"CLOB API error: {e}")

    return None


def extract_btc_target(question: str, description: str) -> Optional[float]:
    """
    Parse target BTC price from market question/description.
    Target is between $10,000 and $500,000.
    """
    text = f"{question} {description}"
    numbers = re.findall(r'\d+(?:\.\d+)?', text)

    for num_str in numbers:
        try:
            num = float(num_str)
            if 10000 <= num <= 500000:
                return num
        except ValueError:
            pass

    return None