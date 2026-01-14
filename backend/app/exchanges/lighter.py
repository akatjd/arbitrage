import aiohttp
from typing import Optional, List
from datetime import datetime
import logging

from app.exchanges.base_futures import BaseFuturesExchange
from app.models.funding import FundingRateInfo, ExchangeType

logger = logging.getLogger(__name__)


class LighterExchange(BaseFuturesExchange):
    """Lighter DEX API 래퍼 (직접 구현 - CCXT 미지원)"""

    BASE_URL = "https://mainnet.zklighter.com/api"

    def __init__(self):
        super().__init__()
        self.name = "Lighter"
        self.exchange_type = ExchangeType.LIGHTER
        self.funding_interval_hours = 1  # Lighter는 1시간 주기
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info("Initialized Lighter exchange")

    async def _get_session(self) -> aiohttp.ClientSession:
        """HTTP 세션 가져오기 (재사용)"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    def _convert_symbol(self, symbol: str) -> str:
        """
        CCXT 형식 심볼을 Lighter 형식으로 변환
        BTC/USDT:USDT -> btc_usdt
        """
        base = symbol.split('/')[0].lower()
        return f"{base}_usdt"

    def _to_ccxt_symbol(self, lighter_symbol: str) -> str:
        """
        Lighter 형식을 CCXT 형식으로 변환
        btc_usdt -> BTC/USDT:USDT
        """
        base = lighter_symbol.split('_')[0].upper()
        return f"{base}/USDT:USDT"

    async def fetch_funding_rate(self, symbol: str) -> Optional[FundingRateInfo]:
        """특정 심볼의 펀딩 레이트 조회"""
        try:
            session = await self._get_session()
            lighter_symbol = self._convert_symbol(symbol)

            # Lighter API 호출
            async with session.get(
                f"{self.BASE_URL}/v1/markets",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    markets = data.get('markets', data) if isinstance(data, dict) else data

                    for market in markets:
                        market_symbol = market.get('symbol', '').lower()
                        if market_symbol == lighter_symbol or market_symbol == lighter_symbol.replace('_', ''):
                            funding_rate = float(market.get('funding_rate', 0) or market.get('fundingRate', 0) or 0)
                            mark_price = float(market.get('mark_price', 0) or market.get('markPrice', 0) or 0)
                            index_price = float(market.get('index_price', 0) or market.get('indexPrice', 0) or 0)

                            return FundingRateInfo(
                                exchange=ExchangeType.LIGHTER,
                                symbol=symbol,
                                funding_rate=funding_rate,
                                funding_interval_hours=self.funding_interval_hours,
                                next_funding_time=None,
                                mark_price=mark_price,
                                index_price=index_price,
                                timestamp=datetime.now()
                            )
                    logger.warning(f"Symbol {symbol} not found in Lighter markets")
                    return None
                else:
                    logger.error(f"Lighter API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Lighter funding rate error for {symbol}: {e}")
            return None

    async def fetch_all_funding_rates(self) -> List[FundingRateInfo]:
        """모든 마켓의 펀딩 레이트 조회"""
        rates = []
        try:
            session = await self._get_session()

            async with session.get(
                f"{self.BASE_URL}/v1/markets",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    markets = data.get('markets', data) if isinstance(data, dict) else data

                    for market in markets:
                        try:
                            symbol_raw = market.get('symbol', '')
                            ccxt_symbol = self._to_ccxt_symbol(symbol_raw)

                            funding_rate = float(market.get('funding_rate', 0) or market.get('fundingRate', 0) or 0)
                            mark_price = float(market.get('mark_price', 0) or market.get('markPrice', 0) or 0)
                            index_price = float(market.get('index_price', 0) or market.get('indexPrice', 0) or 0)

                            info = FundingRateInfo(
                                exchange=ExchangeType.LIGHTER,
                                symbol=ccxt_symbol,
                                funding_rate=funding_rate,
                                funding_interval_hours=self.funding_interval_hours,
                                next_funding_time=None,
                                mark_price=mark_price,
                                index_price=index_price,
                                timestamp=datetime.now()
                            )
                            rates.append(info)
                        except Exception as e:
                            logger.debug(f"Skipping market due to error: {e}")
                            continue
        except Exception as e:
            logger.error(f"Error fetching all Lighter funding rates: {e}")
        return rates

    async def get_supported_symbols(self) -> List[str]:
        """지원하는 심볼 목록 조회"""
        try:
            session = await self._get_session()

            async with session.get(
                f"{self.BASE_URL}/v1/markets",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    markets = data.get('markets', data) if isinstance(data, dict) else data

                    symbols = []
                    for market in markets:
                        symbol_raw = market.get('symbol', '')
                        ccxt_symbol = self._to_ccxt_symbol(symbol_raw)
                        symbols.append(ccxt_symbol)
                    return symbols
                else:
                    return []
        except Exception as e:
            logger.error(f"Error fetching Lighter symbols: {e}")
            return []

    async def close(self):
        """연결 종료"""
        try:
            if self.session and not self.session.closed:
                await self.session.close()
            logger.info("Lighter connection closed")
        except Exception as e:
            logger.error(f"Error closing Lighter connection: {e}")
