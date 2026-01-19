import ccxt.async_support as ccxt
import aiohttp
from typing import Optional, List, Dict
from datetime import datetime
import logging

from app.exchanges.base_futures import BaseFuturesExchange
from app.models.funding import FundingRateInfo, ExchangeType

logger = logging.getLogger(__name__)


class BinanceFutures(BaseFuturesExchange):
    """Binance Futures API 래퍼 (CCXT 사용)"""

    def __init__(self, api_key: str = None, secret: str = None):
        super().__init__()
        self.name = "Binance"
        self.exchange_type = ExchangeType.BINANCE
        self.funding_interval_hours = 8  # Default
        self._funding_intervals: Dict[str, int] = {}  # Symbol -> interval hours cache
        self._intervals_loaded = False

        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',  # Perpetual Futures
            }
        })
        logger.info("Initialized Binance Futures exchange")

    async def _load_funding_intervals(self):
        """각 심볼별 펀딩 간격 로드"""
        if self._intervals_loaded:
            return

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://fapi.binance.com/fapi/v1/fundingInfo',
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        for item in data:
                            symbol = item.get('symbol', '')
                            interval = item.get('fundingIntervalHours', 8)
                            # BERAUSDT -> BERA/USDT:USDT 형식으로 변환
                            if symbol.endswith('USDT'):
                                base = symbol[:-4]
                                ccxt_symbol = f"{base}/USDT:USDT"
                                self._funding_intervals[ccxt_symbol] = interval
                        self._intervals_loaded = True
                        logger.info(f"Loaded {len(self._funding_intervals)} Binance funding intervals")
        except Exception as e:
            logger.warning(f"Failed to load Binance funding intervals: {e}")

    def _get_funding_interval(self, symbol: str) -> int:
        """심볼별 펀딩 간격 반환"""
        return self._funding_intervals.get(symbol, self.funding_interval_hours)

    async def fetch_funding_rate(self, symbol: str) -> Optional[FundingRateInfo]:
        """특정 심볼의 펀딩 레이트 조회"""
        try:
            # 펀딩 간격 정보 로드
            await self._load_funding_intervals()

            # CCXT fetch_funding_rate 사용
            funding = await self.exchange.fetch_funding_rate(symbol)

            next_funding_time = None
            if funding.get('fundingTimestamp'):
                next_funding_time = datetime.fromtimestamp(
                    funding['fundingTimestamp'] / 1000
                )

            # 심볼별 펀딩 간격 사용
            interval = self._get_funding_interval(symbol)

            return FundingRateInfo(
                exchange=ExchangeType.BINANCE,
                symbol=symbol,
                funding_rate=funding.get('fundingRate', 0) or 0,
                funding_interval_hours=interval,
                next_funding_time=next_funding_time,
                mark_price=funding.get('markPrice', 0) or 0,
                index_price=funding.get('indexPrice', 0) or 0,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Binance funding rate error for {symbol}: {e}")
            return None

    async def fetch_all_funding_rates(self) -> List[FundingRateInfo]:
        """모든 영구선물 펀딩 레이트 조회"""
        rates = []
        try:
            # 펀딩 간격 정보 로드
            await self._load_funding_intervals()

            funding_rates = await self.exchange.fetch_funding_rates()

            for symbol, data in funding_rates.items():
                # USDT 마진 선물만 필터링
                if ':USDT' in symbol:
                    # 심볼별 펀딩 간격 사용
                    interval = self._get_funding_interval(symbol)

                    info = FundingRateInfo(
                        exchange=ExchangeType.BINANCE,
                        symbol=symbol,
                        funding_rate=data.get('fundingRate', 0) or 0,
                        funding_interval_hours=interval,
                        next_funding_time=None,
                        mark_price=data.get('markPrice', 0) or 0,
                        index_price=data.get('indexPrice', 0) or 0,
                        timestamp=datetime.now()
                    )
                    rates.append(info)
        except Exception as e:
            logger.error(f"Error fetching all Binance funding rates: {e}")
        return rates

    async def get_supported_symbols(self) -> List[str]:
        """지원하는 심볼 목록 조회"""
        try:
            markets = await self.exchange.load_markets()
            symbols = [
                symbol for symbol, market in markets.items()
                if market.get('swap') and market.get('linear') and ':USDT' in symbol
            ]
            return symbols
        except Exception as e:
            logger.error(f"Error fetching Binance symbols: {e}")
            return []

    async def close(self):
        """연결 종료"""
        try:
            await self.exchange.close()
            logger.info("Binance Futures connection closed")
        except Exception as e:
            logger.error(f"Error closing Binance connection: {e}")
