from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import logging

from app.models.funding import FundingRateInfo, ExchangeType

logger = logging.getLogger(__name__)


class BaseFuturesExchange(ABC):
    """선물 거래소 기본 클래스"""

    def __init__(self):
        self.name: str = ""
        self.exchange_type: ExchangeType = None
        self.funding_interval_hours: int = 8  # 기본 8시간

    @abstractmethod
    async def fetch_funding_rate(self, symbol: str) -> Optional[FundingRateInfo]:
        """
        특정 심볼의 펀딩 레이트 조회

        Args:
            symbol: 거래 심볼 (예: "BTC/USDT:USDT")

        Returns:
            FundingRateInfo 또는 None
        """
        pass

    @abstractmethod
    async def fetch_all_funding_rates(self) -> List[FundingRateInfo]:
        """
        모든 심볼의 펀딩 레이트 조회

        Returns:
            FundingRateInfo 리스트
        """
        pass

    @abstractmethod
    async def get_supported_symbols(self) -> List[str]:
        """
        지원하는 심볼 목록 조회

        Returns:
            심볼 문자열 리스트
        """
        pass

    @abstractmethod
    async def close(self):
        """연결 종료"""
        pass

    def get_funding_interval(self) -> int:
        """펀딩 주기 반환 (시간)"""
        return self.funding_interval_hours
