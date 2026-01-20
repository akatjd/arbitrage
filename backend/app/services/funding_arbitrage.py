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

        APR 계산 방식 (arb69 동일):
        - 펀딩 스프레드 기준으로 단순 연환산
        - APR = spread * 하루 펀딩 횟수 * 365 * 100
        """
        # 필요 증거금 계산 (양쪽 포지션 모두 고려)
        required_margin = (request.position_size_usdt / request.leverage) * 2

        # 펀딩 레이트 값
        long_rate_value = long_rate.funding_rate
        short_rate_value = short_rate.funding_rate

        # 펀딩 레이트 스프레드 (Short에서 받고 Long에서 지불하는 차이)
        # Short 포지션: 양수 펀딩이면 수령, 음수면 지불
        # Long 포지션: 양수 펀딩이면 지불, 음수면 수령
        # 스프레드 = Short 수령 - Long 지불 = short_rate - long_rate
        funding_rate_spread = short_rate_value - long_rate_value

        # 거래소별 펀딩 주기 (시간)
        long_interval = long_rate.funding_interval_hours
        short_interval = short_rate.funding_interval_hours

        # 하루 펀딩 횟수 (Short 거래소 기준 - 펀딩을 받는 쪽)
        # arb69 방식: Short 거래소의 펀딩 주기 사용
        funding_per_day = 24 // short_interval if short_interval > 0 else 3

        # 보유 기간 동안 펀딩 횟수 (Short 거래소 기준)
        total_funding_count = request.holding_period_hours // short_interval if short_interval > 0 else request.holding_period_hours // 8

        # 1회당 펀딩 수익 (USDT)
        per_funding_profit = funding_rate_spread * request.position_size_usdt

        # 총 수익
        total_profit = per_funding_profit * total_funding_count

        # 수익률 계산 (증거금 대비)
        profit_percent = (total_profit / required_margin) * 100 if required_margin > 0 else 0

        # APR 계산 (arb69 방식: 스프레드 * 하루 펀딩 횟수 * 365)
        apr = abs(funding_rate_spread) * funding_per_day * 365 * 100

        # 가격 스프레드 계산
        min_price = min(long_rate.mark_price, short_rate.mark_price) if long_rate.mark_price > 0 and short_rate.mark_price > 0 else max(long_rate.mark_price, short_rate.mark_price)
        price_spread = abs(long_rate.mark_price - short_rate.mark_price)
        price_spread_percent = (price_spread / min_price) * 100 if min_price > 0 else 0

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
            total_funding_count=int(total_funding_count),
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

        # 유효한 데이터만 필터링 (펀딩 레이트가 있는 것만, mark_price=0도 허용)
        valid_rates = {k: v for k, v in all_rates.items() if v.funding_rate is not None}

        if len(valid_rates) < 2:
            logger.warning(f"Not enough valid exchanges with data for {symbol} (valid: {len(valid_rates)}, total: {len(all_rates)})")
            return []

        all_rates = valid_rates

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

            # 1시간 기준으로 정규화된 펀딩 레이트 계산
            long_interval = best_long_rate.funding_interval_hours
            short_interval = best_short_rate.funding_interval_hours

            # 펀딩 레이트를 1시간 기준으로 환산 (예: 8시간 주기 0.01% -> 1시간 기준 0.00125%)
            long_rate_hourly = best.long_funding_rate / long_interval if long_interval > 0 else best.long_funding_rate
            short_rate_hourly = best.short_funding_rate / short_interval if short_interval > 0 else best.short_funding_rate

            # 1시간 기준 스프레드 계산
            funding_spread_hourly = short_rate_hourly - long_rate_hourly

            opportunities.append(TopArbitrageOpportunity(
                rank=0,
                symbol=symbol,
                long_exchange=best.long_exchange,
                short_exchange=best.short_exchange,
                long_funding_rate=best.long_funding_rate,
                short_funding_rate=best.short_funding_rate,
                long_funding_interval=long_interval,
                short_funding_interval=short_interval,
                long_funding_rate_hourly=round(long_rate_hourly, 8),
                short_funding_rate_hourly=round(short_rate_hourly, 8),
                funding_spread=best.funding_rate_spread,
                funding_spread_hourly=round(funding_spread_hourly, 8),
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
