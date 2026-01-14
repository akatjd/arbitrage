from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime


class ExchangeType(str, Enum):
    """지원하는 거래소 타입"""
    BINANCE = "binance"
    BYBIT = "bybit"
    HYPERLIQUID = "hyperliquid"
    LIGHTER = "lighter"


class FundingRateInfo(BaseModel):
    """펀딩 레이트 정보"""
    exchange: ExchangeType
    symbol: str
    funding_rate: float  # 현재 펀딩 레이트 (예: 0.0001 = 0.01%)
    funding_interval_hours: int  # 펀딩 주기 (시간)
    next_funding_time: Optional[datetime] = None
    mark_price: float
    index_price: float
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FundingArbitrageRequest(BaseModel):
    """아비트리지 계산 요청"""
    symbol: str  # 예: "BTC/USDT:USDT"
    long_exchange: ExchangeType
    short_exchange: ExchangeType
    position_size_usdt: float  # 포지션 규모 (USDT)
    leverage: float = 1.0  # 레버리지
    holding_period_hours: int = 24  # 보유 기간 (시간)


class FundingArbitrageResult(BaseModel):
    """아비트리지 계산 결과"""
    symbol: str
    long_exchange: ExchangeType
    short_exchange: ExchangeType

    # 펀딩 레이트 정보
    long_funding_rate: float  # Long 거래소 펀딩 레이트
    short_funding_rate: float  # Short 거래소 펀딩 레이트
    funding_rate_spread: float  # 펀딩 레이트 차이

    # 가격 정보
    long_mark_price: float
    short_mark_price: float
    price_spread_percent: float  # 가격 스프레드 (%)

    # 수익 계산
    per_funding_profit_usdt: float  # 1회 펀딩당 수익 (USDT)
    total_funding_count: int  # 총 펀딩 횟수
    estimated_total_profit_usdt: float  # 예상 총 수익 (USDT)
    estimated_profit_percent: float  # 예상 수익률 (%)
    apr: float  # 연환산 수익률 (%)

    # 입력값
    position_size_usdt: float
    leverage: float
    holding_period_hours: int
    required_margin_usdt: float  # 필요 증거금

    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TopArbitrageOpportunity(BaseModel):
    """상위 아비트리지 기회"""
    rank: int
    symbol: str
    long_exchange: ExchangeType
    short_exchange: ExchangeType
    long_funding_rate: float
    short_funding_rate: float
    funding_spread: float
    estimated_apr: float  # 기본 설정 기준 APR
    long_mark_price: float
    short_mark_price: float
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
