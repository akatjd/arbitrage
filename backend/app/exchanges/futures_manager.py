from typing import Dict, List, Optional
import logging
import asyncio

from app.exchanges.base_futures import BaseFuturesExchange
from app.exchanges.binance_futures import BinanceFutures
from app.exchanges.bybit_futures import BybitFutures
from app.exchanges.hyperliquid import HyperliquidExchange
from app.exchanges.lighter import LighterExchange
from app.models.funding import FundingRateInfo, ExchangeType

logger = logging.getLogger(__name__)


class FuturesManager:
    """모든 선물 거래소 통합 관리"""

    # 거래소별 펀딩 주기 (시간)
    FUNDING_INTERVALS = {
        ExchangeType.BINANCE: 8,
        ExchangeType.BYBIT: 8,
        ExchangeType.HYPERLIQUID: 1,
        ExchangeType.LIGHTER: 1,
    }

    def __init__(self, config: dict = None):
        self.exchanges: Dict[ExchangeType, BaseFuturesExchange] = {}
        self.config = config or {}
        self._initialized = False

    async def initialize(self):
        """거래소 초기화 (비동기)"""
        if self._initialized:
            return

        logger.info("Initializing futures exchanges...")

        # Binance Futures
        try:
            self.exchanges[ExchangeType.BINANCE] = BinanceFutures(
                api_key=self.config.get('binance_api_key'),
                secret=self.config.get('binance_secret')
            )
            logger.info("Binance Futures initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Binance Futures: {e}")

        # Bybit Futures
        try:
            self.exchanges[ExchangeType.BYBIT] = BybitFutures(
                api_key=self.config.get('bybit_api_key'),
                secret=self.config.get('bybit_secret')
            )
            logger.info("Bybit Futures initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Bybit Futures: {e}")

        # Hyperliquid
        try:
            self.exchanges[ExchangeType.HYPERLIQUID] = HyperliquidExchange(
                wallet_address=self.config.get('hyperliquid_wallet'),
                private_key=self.config.get('hyperliquid_private_key')
            )
            logger.info("Hyperliquid initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Hyperliquid: {e}")

        # Lighter - 현재 API 비활성화 상태로 비활성화
        # try:
        #     self.exchanges[ExchangeType.LIGHTER] = LighterExchange()
        #     logger.info("Lighter initialized")
        # except Exception as e:
        #     logger.error(f"Failed to initialize Lighter: {e}")

        self._initialized = True
        logger.info(f"Futures Manager initialized with {len(self.exchanges)} exchanges")

    async def get_funding_rate(
        self,
        exchange: ExchangeType,
        symbol: str
    ) -> Optional[FundingRateInfo]:
        """특정 거래소의 펀딩 레이트 조회"""
        if exchange not in self.exchanges:
            logger.warning(f"Exchange {exchange} not available")
            return None

        return await self.exchanges[exchange].fetch_funding_rate(symbol)

    async def get_all_funding_rates(
        self,
        symbol: str
    ) -> Dict[ExchangeType, FundingRateInfo]:
        """모든 거래소에서 특정 심볼의 펀딩 레이트 조회 (병렬)"""
        result = {}

        async def fetch_rate(exchange_type: ExchangeType):
            try:
                rate = await self.exchanges[exchange_type].fetch_funding_rate(symbol)
                if rate:
                    return exchange_type, rate
            except Exception as e:
                logger.error(f"Error fetching {symbol} from {exchange_type}: {e}")
            return exchange_type, None

        # 병렬로 모든 거래소에서 조회
        tasks = [fetch_rate(ex_type) for ex_type in self.exchanges.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in results:
            if isinstance(res, tuple) and res[1] is not None:
                result[res[0]] = res[1]

        return result

    def get_funding_interval(self, exchange: ExchangeType) -> int:
        """거래소별 펀딩 주기 반환 (시간)"""
        return self.FUNDING_INTERVALS.get(exchange, 8)

    def get_available_exchanges(self) -> List[ExchangeType]:
        """사용 가능한 거래소 목록"""
        return list(self.exchanges.keys())

    def get_exchange_info(self) -> List[dict]:
        """거래소 정보 목록"""
        return [
            {
                "id": ex_type.value,
                "name": self.exchanges[ex_type].name,
                "funding_interval": self.get_funding_interval(ex_type)
            }
            for ex_type in self.exchanges.keys()
        ]

    async def close_all(self):
        """모든 거래소 연결 종료"""
        for exchange_type, exchange in self.exchanges.items():
            try:
                await exchange.close()
                logger.info(f"Closed {exchange_type} connection")
            except Exception as e:
                logger.error(f"Error closing {exchange_type}: {e}")
