"""Order placement and management"""

from py_clob_client.client import ClobClient
from py_clob_client.order_args import OrderArgs, OrderType

from src.config import BotConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


def place_order(
    token_id: str,
    price: float,
    size: float,
    side: str,
    config: BotConfig
) -> str:
    """
    Place a limit order on CLOB.
    Returns order_id on success, or "SIM_ORDER" in dry run.
    """
    if config.dry_run:
        logger.info(f"[SIM] {side} {size:.2f} USDC @ {price:.3f}")
        return "SIM_ORDER"

    try:
        client = ClobClient(
            host=config.clob_host,
            key=config.private_key,
            chain_id=config.chain_id
        )
        creds = client.create_or_derive_api_creds()
        client.set_api_creds(creds)

        # Cross the spread slightly
        if side == "BUY":
            order_price = price - 0.005
        else:
            order_price = price + 0.005

        order_args = OrderArgs(
            token_id=token_id,
            price=order_price,
            size=size,
            side=side,
            order_type=OrderType.GTC,
        )
        result = client.create_order(order_args)
        order_id = result.get("order_id", "")
        logger.info(f"[ORDER] {side} {size:.2f} @ {order_price:.3f} (id: {order_id})")
        return order_id
    except Exception as e:
        logger.error(f"Order placement failed: {e}")
        return ""


def cancel_order(order_id: str, config: BotConfig) -> None:
    """Cancel an order on CLOB"""
    if config.dry_run:
        logger.info(f"[SIM] CANCEL {order_id}")
        return

    try:
        client = ClobClient(
            host=config.clob_host,
            key=config.private_key,
            chain_id=config.chain_id
        )
        creds = client.create_or_derive_api_creds()
        client.set_api_creds(creds)
        client.cancel_order(order_id)
        logger.info(f"[CANCEL] {order_id}")
    except Exception as e:
        logger.error(f"Cancel failed: {e}")