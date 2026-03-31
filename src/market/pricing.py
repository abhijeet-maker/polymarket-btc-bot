"""Price fetching and management"""

from typing import Tuple

import requests

from src.config import BotConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


def fetch_order_book(
    token_id: str,
    config: BotConfig
) -> Tuple[float, float]:
    """
    Fetch order book and return mid-price.
    Returns (mid, mid) on success, (0.0, 0.0) on error.
    """
    try:
        resp = requests.get(
            f"{config.clob_host}/book?token_id={token_id}",
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            bids = data.get("bids", [])
            asks = data.get("asks", [])

            if bids and asks:
                best_bid = float(bids[0].get("price", 0.0))
                best_ask = float(asks[0].get("price", 0.0))
                mid = (best_bid + best_ask) / 2.0
                return mid, mid
    except Exception as e:
        logger.debug(f"Order book fetch error: {e}")

    return 0.0, 0.0