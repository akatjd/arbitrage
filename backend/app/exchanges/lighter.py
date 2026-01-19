import aiohttp
import ssl
from typing import Optional, List, Dict
from datetime import datetime
import logging

from app.exchanges.base_futures import BaseFuturesExchange
from app.models.funding import FundingRateInfo, ExchangeType

logger = logging.getLogger(__name__)


class LighterExchange(BaseFuturesExchange):
    """Lighter DEX API 래퍼 (직접 구현 - CCXT 미지원)"""

    BASE_URL = "https://mainnet.zklighter.elliot.ai/api"

    def __init__(self):
        super().__init__()
        self.name = "Lighter"
        self.exchange_type = ExchangeType.LIGHTER
        self.funding_interval_hours = 1  # Lighter는 1시간 주기
        self.session: Optional[aiohttp.ClientSession] = None
        self._funding_rates_cache: Dict[str, dict] = {}
        self._cache_time: Optional[datetime] = None
        self._cache_ttl_seconds = 30  # 30초 캐시
        logger.info("Initialized Lighter exchange")

    async def _get_session(self) -> aiohttp.ClientSession:
        """HTTP 세션 가져오기 (재사용)"""
        if self.session is None or self.session.closed:
            # SSL 검증 비활성화 (인증서 문제 해결)
            connector = aiohttp.TCPConnector(ssl=False)
            self.session = aiohttp.ClientSession(connector=connector)
        return self.session

    def _convert_symbol_to_lighter(self, symbol: str) -> str:
        """
        CCXT 형식 심볼을 Lighter 형식으로 변환
        BTC/USDT:USDT -> BTC
        1000PEPE/USDT:USDT -> 1000PEPE
        """
        base = symbol.split('/')[0]
        return base

    def _convert_symbol_to_ccxt(self, lighter_symbol: str) -> str:
        """
        Lighter 형식을 CCXT 형식으로 변환
        BTC -> BTC/USDT:USDT
        """
        return f"{lighter_symbol}/USDT:USDT"

    async def _fetch_all_rates(self) -> Dict[str, dict]:
        """모든 펀딩 레이트 조회 (캐시 사용)"""
        now = datetime.now()

        # 캐시가 유효하면 반환
        if (self._cache_time and
            (now - self._cache_time).total_seconds() < self._cache_ttl_seconds and
            self._funding_rates_cache):
            return self._funding_rates_cache

        try:
            session = await self._get_session()

            async with session.get(
                f"{self.BASE_URL}/v1/funding-rates",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    funding_rates = data.get('funding_rates', [])

                    # Lighter 거래소 데이터만 필터링하여 캐시
                    self._funding_rates_cache = {}
                    for rate in funding_rates:
                        if rate.get('exchange') == 'lighter':
                            symbol = rate.get('symbol', '')
                            self._funding_rates_cache[symbol] = rate

                    self._cache_time = now
                    logger.debug(f"Fetched {len(self._funding_rates_cache)} Lighter funding rates")
                    return self._funding_rates_cache
                else:
                    logger.error(f"Lighter API error: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error fetching Lighter funding rates: {e}")
            return {}

    async def fetch_funding_rate(self, symbol: str) -> Optional[FundingRateInfo]:
        """특정 심볼의 펀딩 레이트 조회"""
        try:
            lighter_symbol = self._convert_symbol_to_lighter(symbol)
            rates = await self._fetch_all_rates()

            if lighter_symbol not in rates:
                logger.debug(f"Symbol {lighter_symbol} not found in Lighter markets")
                return None

            rate_data = rates[lighter_symbol]
            funding_rate = float(rate_data.get('rate', 0) or 0)

            return FundingRateInfo(
                exchange=ExchangeType.LIGHTER,
                symbol=symbol,
                funding_rate=funding_rate,
                funding_interval_hours=self.funding_interval_hours,
                next_funding_time=None,
                mark_price=0,  # API에서 제공하지 않음
                index_price=0,  # API에서 제공하지 않음
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Lighter funding rate error for {symbol}: {e}")
            return None

    async def fetch_all_funding_rates(self) -> List[FundingRateInfo]:
        """모든 마켓의 펀딩 레이트 조회"""
        rates_list = []
        try:
            rates = await self._fetch_all_rates()

            for symbol, rate_data in rates.items():
                try:
                    ccxt_symbol = self._convert_symbol_to_ccxt(symbol)
                    funding_rate = float(rate_data.get('rate', 0) or 0)

                    info = FundingRateInfo(
                        exchange=ExchangeType.LIGHTER,
                        symbol=ccxt_symbol,
                        funding_rate=funding_rate,
                        funding_interval_hours=self.funding_interval_hours,
                        next_funding_time=None,
                        mark_price=0,
                        index_price=0,
                        timestamp=datetime.now()
                    )
                    rates_list.append(info)
                except Exception as e:
                    logger.debug(f"Skipping market {symbol} due to error: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error fetching all Lighter funding rates: {e}")
        return rates_list

    async def get_supported_symbols(self) -> List[str]:
        """지원하는 심볼 목록 조회"""
        try:
            rates = await self._fetch_all_rates()
            return [self._convert_symbol_to_ccxt(s) for s in rates.keys()]
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
