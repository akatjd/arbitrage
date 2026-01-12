from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ArbitrageCalculator:
    """아비트라지 기회 계산 서비스"""

    def __init__(self, usd_to_krw_rate: float = 1300):
        """
        Args:
            usd_to_krw_rate: USD/KRW 환율 (기본값: 1300)
        """
        self.usd_to_krw_rate = usd_to_krw_rate

    def update_exchange_rate(self, rate: float):
        """환율 업데이트"""
        self.usd_to_krw_rate = rate
        logger.info(f"Exchange rate updated to: {rate}")

    def calculate_arbitrage(
        self,
        binance_ticker: Dict,
        upbit_ticker: Dict,
        binance_fee: Dict[str, float],
        upbit_fee: Dict[str, float],
        transfer_fee_percent: float = 0.001  # 송금 수수료 0.1%
    ) -> Optional[Dict]:
        """
        두 거래소 간의 아비트라지 기회 계산

        Args:
            binance_ticker: 바이낸스 티커 데이터
            upbit_ticker: 업비트 티커 데이터
            binance_fee: 바이낸스 거래 수수료
            upbit_fee: 업비트 거래 수수료
            transfer_fee_percent: 송금 수수료 (기본값 0.1%)

        Returns:
            아비트라지 정보 딕셔너리
        """
        if not binance_ticker or not upbit_ticker:
            return None

        try:
            # 가격 데이터 검증
            if (binance_ticker.get('ask') is None or binance_ticker.get('bid') is None or
                upbit_ticker.get('ask') is None or upbit_ticker.get('bid') is None):
                return None

            # 바이낸스 가격 (USDT)을 KRW로 변환
            binance_price_krw = binance_ticker['ask'] * self.usd_to_krw_rate
            upbit_price_krw = upbit_ticker['bid']

            # 케이스 1: 바이낸스에서 사고 업비트에서 팔기
            buy_binance_cost = binance_price_krw * (1 + binance_fee['taker'])
            sell_upbit_revenue = upbit_price_krw * (1 - upbit_fee['taker'])
            profit_binance_to_upbit = sell_upbit_revenue - buy_binance_cost
            profit_percent_b_to_u = (profit_binance_to_upbit / buy_binance_cost) * 100 - transfer_fee_percent * 100

            # 케이스 2: 업비트에서 사고 바이낸스에서 팔기
            buy_upbit_cost = upbit_price_krw * (1 + upbit_fee['taker'])
            sell_binance_revenue = binance_price_krw * (1 - binance_fee['taker'])
            profit_upbit_to_binance = sell_binance_revenue - buy_upbit_cost
            profit_percent_u_to_b = (profit_upbit_to_binance / buy_upbit_cost) * 100 - transfer_fee_percent * 100

            # 최적의 방향 결정
            if profit_percent_b_to_u > profit_percent_u_to_b:
                direction = "Binance → Upbit"
                profit_percent = profit_percent_b_to_u
                buy_price = buy_binance_cost
                sell_price = sell_upbit_revenue
            else:
                direction = "Upbit → Binance"
                profit_percent = profit_percent_u_to_b
                buy_price = buy_upbit_cost
                sell_price = sell_binance_revenue

            # 김치 프리미엄 계산 (수수료 제외한 단순 가격 차이)
            raw_premium_percent = ((upbit_price_krw - binance_price_krw) / binance_price_krw) * 100

            return {
                'symbol': binance_ticker['symbol'],
                'direction': direction,
                'profit_percent': round(profit_percent, 4),
                'raw_premium_percent': round(raw_premium_percent, 4),  # 김치 프리미엄
                'binance_price_usd': round(binance_ticker['ask'], 2),
                'binance_price_krw': round(binance_price_krw, 2),
                'upbit_price_krw': round(upbit_price_krw, 2),
                'buy_price': round(buy_price, 2),
                'sell_price': round(sell_price, 2),
                'exchange_rate': self.usd_to_krw_rate,
                'timestamp': binance_ticker['timestamp'],
                'is_profitable': profit_percent > 0
            }

        except Exception as e:
            logger.error(f"Error calculating arbitrage: {e}")
            return None

    def calculate_profit_for_amount(
        self,
        arbitrage_data: Dict,
        amount: float
    ) -> Dict:
        """
        특정 금액에 대한 예상 수익 계산

        Args:
            arbitrage_data: calculate_arbitrage의 결과
            amount: 투자 금액 (KRW)

        Returns:
            예상 수익 정보
        """
        if not arbitrage_data or not arbitrage_data['is_profitable']:
            return {
                'investment': amount,
                'expected_profit': 0,
                'expected_return': amount,
                'profit_percent': 0
            }

        profit = amount * (arbitrage_data['profit_percent'] / 100)
        return {
            'investment': amount,
            'expected_profit': round(profit, 2),
            'expected_return': round(amount + profit, 2),
            'profit_percent': arbitrage_data['profit_percent']
        }
