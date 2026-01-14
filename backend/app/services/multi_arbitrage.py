from typing import Dict, List, Optional
import logging
from itertools import combinations

logger = logging.getLogger(__name__)


class MultiArbitrageCalculator:
    """여러 거래소 간 아비트라지 계산 서비스"""

    def __init__(self, usd_to_krw_rate: float = 1300):
        self.usd_to_krw_rate = usd_to_krw_rate

    def update_exchange_rate(self, rate: float):
        """환율 업데이트"""
        self.usd_to_krw_rate = rate
        logger.info(f"Exchange rate updated to: {rate}")

    def calculate_arbitrage_opportunities(
        self,
        tickers: Dict[str, Dict],  # {exchange_name: ticker_data}
        fees: Dict[str, Dict[str, float]],  # {exchange_name: {maker, taker}}
        transfer_fee_percent: float = 0.001
    ) -> List[Dict]:
        """
        모든 거래소 쌍 간의 아비트라지 기회 계산

        Args:
            tickers: 거래소별 티커 데이터
            fees: 거래소별 수수료
            transfer_fee_percent: 송금 수수료

        Returns:
            아비트라지 기회 리스트 (수익률 순으로 정렬)
        """
        opportunities = []
        exchanges = list(tickers.keys())

        # 모든 거래소 쌍에 대해 계산
        for exchange1, exchange2 in combinations(exchanges, 2):
            ticker1 = tickers[exchange1]
            ticker2 = tickers[exchange2]

            if not ticker1 or not ticker2:
                continue

            # 두 방향 모두 계산
            # 방향 1: exchange1에서 매수 -> exchange2에서 매도
            opp1 = self._calculate_single_arbitrage(
                buy_exchange=exchange1,
                sell_exchange=exchange2,
                buy_ticker=ticker1,
                sell_ticker=ticker2,
                buy_fee=fees.get(exchange1, {'maker': 0.002, 'taker': 0.002}),
                sell_fee=fees.get(exchange2, {'maker': 0.002, 'taker': 0.002}),
                transfer_fee_percent=transfer_fee_percent
            )
            if opp1:
                opportunities.append(opp1)

            # 방향 2: exchange2에서 매수 -> exchange1에서 매도
            opp2 = self._calculate_single_arbitrage(
                buy_exchange=exchange2,
                sell_exchange=exchange1,
                buy_ticker=ticker2,
                sell_ticker=ticker1,
                buy_fee=fees.get(exchange2, {'maker': 0.002, 'taker': 0.002}),
                sell_fee=fees.get(exchange1, {'maker': 0.002, 'taker': 0.002}),
                transfer_fee_percent=transfer_fee_percent
            )
            if opp2:
                opportunities.append(opp2)

        # 수익률 순으로 정렬 (내림차순)
        opportunities.sort(key=lambda x: x['profit_percent'], reverse=True)
        return opportunities

    def _calculate_single_arbitrage(
        self,
        buy_exchange: str,
        sell_exchange: str,
        buy_ticker: Dict,
        sell_ticker: Dict,
        buy_fee: Dict[str, float],
        sell_fee: Dict[str, float],
        transfer_fee_percent: float
    ) -> Optional[Dict]:
        """
        단일 방향 아비트라지 계산

        Args:
            buy_exchange: 매수 거래소
            sell_exchange: 매도 거래소
            buy_ticker: 매수 거래소 티커
            sell_ticker: 매도 거래소 티커
            buy_fee: 매수 거래소 수수료
            sell_fee: 매도 거래소 수수료
            transfer_fee_percent: 송금 수수료

        Returns:
            아비트라지 정보
        """
        try:
            # 가격 데이터 검증
            if (buy_ticker.get('ask') is None or sell_ticker.get('bid') is None):
                return None

            # 모든 거래소가 USD 기반이므로 USD 가격 사용
            buy_price_usd = buy_ticker['ask']
            sell_price_usd = sell_ticker['bid']

            # 수수료 포함 실제 비용 계산 (USD 기준)
            buy_cost = buy_price_usd * (1 + buy_fee['taker'])
            sell_revenue = sell_price_usd * (1 - sell_fee['taker'])

            # 송금 수수료 차감
            sell_revenue = sell_revenue * (1 - transfer_fee_percent)

            # 수익 계산
            profit = sell_revenue - buy_cost
            profit_percent = (profit / buy_cost) * 100

            # 프리미엄 계산 (수수료 제외한 순수 가격 차이)
            raw_premium_percent = ((sell_price_usd - buy_price_usd) / buy_price_usd) * 100

            # 순수 가격 차이 (수수료 제외)
            price_difference_usd = sell_price_usd - buy_price_usd

            return {
                'symbol': buy_ticker['symbol'],
                'buy_exchange': buy_exchange.upper(),
                'sell_exchange': sell_exchange.upper(),
                'direction': f"{buy_exchange.upper()} → {sell_exchange.upper()}",
                'action': f"LONG @ {buy_exchange.upper()}, SHORT @ {sell_exchange.upper()}",
                'profit_percent': round(profit_percent, 4),
                'raw_premium_percent': round(raw_premium_percent, 4),
                'buy_price_usd': round(buy_price_usd, 4),
                'sell_price_usd': round(sell_price_usd, 4),
                'buy_cost_usd': round(buy_cost, 4),
                'sell_revenue_usd': round(sell_revenue, 4),
                'price_difference_usd': round(price_difference_usd, 4),
                'profit_usd': round(profit, 4),
                'timestamp': buy_ticker['timestamp'],
                'is_profitable': profit_percent > 0
            }

        except Exception as e:
            logger.error(f"Error calculating arbitrage between {buy_exchange} and {sell_exchange}: {e}")
            return None
