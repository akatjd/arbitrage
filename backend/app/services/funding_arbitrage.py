from typing import List, Optional, Dict
from datetime import datetime
from itertools import combinations
import logging

from app.models.funding import (
    FundingRateInfo,
    FundingArbitrageRequest,
    FundingArbitrageResult,
    TopArbitrageOpportunity,
    ExchangeType
)
from app.exchanges.futures_manager import FuturesManager

logger = logging.getLogger(__name__)


class FundingArbitrageService:
    """펀딩 레이트 아비트리지 계산 서비스"""

    def __init__(self, futures_manager: FuturesManager):
        self.futures_manager = futures_manager

    def calculate_arbitrage(
        self,
        request: FundingArbitrageRequest,
        long_rate: FundingRateInfo,
        short_rate: FundingRateInfo
    ) -> FundingArbitrageResult:
        """
        펀딩 아비트리지 수익 계산

        원리:
        - Long 포지션: 펀딩 레이트 > 0 이면 지불, < 0 이면 수령
        - Short 포지션: 펀딩 레이트 > 0 이면 수령, < 0 이면 지불

        전략: Long에서 받고 Short에서 받는 최적 조합 찾기
        """
        # 필요 증거금 계산 (양쪽 포지션 모두 고려)
        required_margin = (request.position_size_usdt / request.leverage) * 2

        # 거래소별 펀딩 주기
        long_interval = self.futures_manager.get_funding_interval(request.long_exchange)
        short_interval = self.futures_manager.get_funding_interval(request.short_exchange)

        # 총 펀딩 횟수 계산
        long_funding_count = request.holding_period_hours // long_interval
        short_funding_count = request.holding_period_hours // short_interval

        # 펀딩 레이트 값
        long_rate_value = long_rate.funding_rate
        short_rate_value = short_rate.funding_rate

        # 1회당 펀딩 수익 계산 (USDT)
        # Long 포지션 수익: -funding_rate * position_size (Long은 양수 펀딩에서 지불)
        # Short 포지션 수익: +funding_rate * position_size (Short은 양수 펀딩에서 수령)
        long_per_funding = -long_rate_value * request.position_size_usdt
        short_per_funding = short_rate_value * request.position_size_usdt

        # 총 펀딩 수익 계산
        total_long_profit = long_per_funding * long_funding_count
        total_short_profit = short_per_funding * short_funding_count
        total_profit = total_long_profit + total_short_profit

        # 평균 펀딩 횟수 (표시용)
        total_funding_count = long_funding_count + short_funding_count
        avg_funding_count = total_funding_count / 2 if total_funding_count > 0 else 1

        # 1회 평균 펀딩 수익
        per_funding_profit = total_profit / avg_funding_count if avg_funding_count > 0 else 0

        # 수익률 계산 (증거금 대비)
        profit_percent = (total_profit / required_margin) * 100 if required_margin > 0 else 0

        # APR 계산 (연환산)
        hours_per_year = 8760  # 365 * 24
        apr = (profit_percent / request.holding_period_hours) * hours_per_year if request.holding_period_hours > 0 else 0

        # 가격 스프레드 계산
        min_price = min(long_rate.mark_price, short_rate.mark_price)
        price_spread = abs(long_rate.mark_price - short_rate.mark_price)
        price_spread_percent = (price_spread / min_price) * 100 if min_price > 0 else 0

        # 펀딩 레이트 스프레드
        funding_rate_spread = short_rate_value - long_rate_value

        return FundingArbitrageResult(
            symbol=request.symbol,
            long_exchange=request.long_exchange,
            short_exchange=request.short_exchange,
            long_funding_rate=long_rate_value,
            short_funding_rate=short_rate_value,
            funding_rate_spread=round(funding_rate_spread, 6),
            long_mark_price=long_rate.mark_price,
            short_mark_price=short_rate.mark_price,
            price_spread_percent=round(price_spread_percent, 4),
            per_funding_profit_usdt=round(per_funding_profit, 4),
            total_funding_count=int(avg_funding_count),
            estimated_total_profit_usdt=round(total_profit, 4),
            estimated_profit_percent=round(profit_percent, 4),
            apr=round(apr, 2),
            position_size_usdt=request.position_size_usdt,
            leverage=request.leverage,
            holding_period_hours=request.holding_period_hours,
            required_margin_usdt=round(required_margin, 2),
            timestamp=datetime.now()
        )

    async def find_top_opportunities(
        self,
        symbol: str,
        default_position: float = 10000,
        default_leverage: float = 2,
        default_hours: int = 24
    ) -> List[TopArbitrageOpportunity]:
        """
        상위 아비트리지 기회 자동 탐색

        모든 거래소 조합에서 최고 수익 기회를 찾음
        """
        # 모든 거래소에서 펀딩 레이트 조회
        all_rates = await self.futures_manager.get_all_funding_rates(symbol)

        if len(all_rates) < 2:
            logger.warning(f"Not enough exchanges with data for {symbol}")
            return []

        opportunities = []
        exchanges = list(all_rates.keys())

        # 모든 거래소 조합에 대해 계산
        for ex1, ex2 in combinations(exchanges, 2):
            rate1 = all_rates[ex1]
            rate2 = all_rates[ex2]

            # 방향 1: ex1에서 Long, ex2에서 Short
            request1 = FundingArbitrageRequest(
                symbol=symbol,
                long_exchange=ex1,
                short_exchange=ex2,
                position_size_usdt=default_position,
                leverage=default_leverage,
                holding_period_hours=default_hours
            )
            result1 = self.calculate_arbitrage(request1, rate1, rate2)

            # 방향 2: ex2에서 Long, ex1에서 Short
            request2 = FundingArbitrageRequest(
                symbol=symbol,
                long_exchange=ex2,
                short_exchange=ex1,
                position_size_usdt=default_position,
                leverage=default_leverage,
                holding_period_hours=default_hours
            )
            result2 = self.calculate_arbitrage(request2, rate2, rate1)

            # 더 좋은 방향 선택
            best = result1 if result1.apr > result2.apr else result2
            best_long_rate = rate1 if result1.apr > result2.apr else rate2
            best_short_rate = rate2 if result1.apr > result2.apr else rate1

            opportunities.append(TopArbitrageOpportunity(
                rank=0,
                symbol=symbol,
                long_exchange=best.long_exchange,
                short_exchange=best.short_exchange,
                long_funding_rate=best.long_funding_rate,
                short_funding_rate=best.short_funding_rate,
                funding_spread=best.funding_rate_spread,
                estimated_apr=best.apr,
                long_mark_price=best_long_rate.mark_price,
                short_mark_price=best_short_rate.mark_price,
                timestamp=datetime.now()
            ))

        # APR 기준 정렬
        opportunities.sort(key=lambda x: x.estimated_apr, reverse=True)

        # 순위 부여
        for i, opp in enumerate(opportunities):
            opp.rank = i + 1

        return opportunities

    async def find_all_opportunities(
        self,
        symbols: List[str],
        default_position: float = 10000,
        default_leverage: float = 2,
        default_hours: int = 24,
        limit: int = 20,
        one_per_symbol: bool = True
    ) -> List[TopArbitrageOpportunity]:
        """
        여러 심볼에서 상위 아비트리지 기회 탐색

        Args:
            one_per_symbol: True면 심볼당 최고 기회 하나만 반환
        """
        all_opportunities = []

        for symbol in symbols:
            try:
                opps = await self.find_top_opportunities(
                    symbol=symbol,
                    default_position=default_position,
                    default_leverage=default_leverage,
                    default_hours=default_hours
                )
                if one_per_symbol and opps:
                    # 심볼당 최고 기회 하나만 추가
                    all_opportunities.append(opps[0])
                else:
                    all_opportunities.extend(opps)
            except Exception as e:
                logger.error(f"Error finding opportunities for {symbol}: {e}")
                continue

        # APR 기준 정렬
        all_opportunities.sort(key=lambda x: x.estimated_apr, reverse=True)

        # 순위 재부여
        for i, opp in enumerate(all_opportunities[:limit]):
            opp.rank = i + 1

        return all_opportunities[:limit]
