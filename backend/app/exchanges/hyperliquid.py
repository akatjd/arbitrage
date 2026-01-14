import ccxt.async_support as ccxt
from typing import Optional, List
from datetime import datetime
import logging

from app.exchanges.base_futures import BaseFuturesExchange
from app.models.funding import FundingRateInfo, ExchangeType

logger = logging.getLogger(__name__)


class HyperliquidExchange(BaseFuturesExchange):
    """Hyperliquid API 래퍼 (CCXT 지원)"""

    def __init__(self, wallet_address: str = None, private_key: str = None):
        super().__init__()
        self.name = "Hyperliquid"
        self.exchange_type = ExchangeType.HYPERLIQUID
        self.funding_interval_hours = 1  # Hyperliquid는 1시간 주기

        config = {
            'enableRateLimit': True,
        }

        # DEX는 지갑 주소 사용 (선택적)
        if wallet_address:
            config['walletAddress'] = wallet_address
        if private_key:
            config['privateKey'] = private_key

        self.exchange = ccxt.hyperliquid(config)
        logger.info("Initialized Hyperliquid exchange")

    async def fetch_funding_rate(self, symbol: str) -> Optional[FundingRateInfo]:
        """특정 심볼의 펀딩 레이트 조회"""
        try:
            funding = await self.exchange.fetch_funding_rate(symbol)

            next_funding_time = None
            if funding.get('fundingTimestamp'):
                next_funding_time = datetime.fromtimestamp(
                    funding['fundingTimestamp'] / 1000
                )

            return FundingRateInfo(
                exchange=ExchangeType.HYPERLIQUID,
                symbol=symbol,
                funding_rate=funding.get('fundingRate', 0) or 0,
                funding_interval_hours=self.funding_interval_hours,
                next_funding_time=next_funding_time,
                mark_price=funding.get('markPrice', 0) or 0,
                index_price=funding.get('indexPrice', 0) or 0,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Hyperliquid funding rate error for {symbol}: {e}")
            return None

    async def fetch_all_funding_rates(self) -> List[FundingRateInfo]:
        """모든 펀딩 레이트 조회"""
        rates = []
        try:
            funding_rates = await self.exchange.fetch_funding_rates()

            for symbol, data in funding_rates.items():
                info = FundingRateInfo(
                    exchange=ExchangeType.HYPERLIQUID,
                    symbol=symbol,
                    funding_rate=data.get('fundingRate', 0) or 0,
                    funding_interval_hours=self.funding_interval_hours,
                    next_funding_time=None,
                    mark_price=data.get('markPrice', 0) or 0,
                    index_price=data.get('indexPrice', 0) or 0,
                    timestamp=datetime.now()
                )
                rates.append(info)
        except Exception as e:
            logger.error(f"Error fetching all Hyperliquid funding rates: {e}")
        return rates

    async def get_supported_symbols(self) -> List[str]:
        """지원하는 심볼 목록 조회"""
        try:
            markets = await self.exchange.load_markets()
            symbols = [symbol for symbol in markets.keys()]
            return symbols
        except Exception as e:
            logger.error(f"Error fetching Hyperliquid symbols: {e}")
            return []

    async def close(self):
        """연결 종료"""
        try:
            await self.exchange.close()
            logger.info("Hyperliquid connection closed")
        except Exception as e:
            logger.error(f"Error closing Hyperliquid connection: {e}")
