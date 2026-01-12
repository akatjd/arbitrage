import ccxt.async_support as ccxt
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class UpbitExchange:
    """업비트 거래소 API 래퍼"""

    def __init__(self, access_key: str = None, secret_key: str = None):
        self.exchange = ccxt.upbit({
            'apiKey': access_key,
            'secret': secret_key,
            'enableRateLimit': True,
        })
        self.name = "Upbit"

    def convert_symbol(self, binance_symbol: str) -> str:
        """
        바이낸스 심볼을 업비트 형식으로 변환
        예: 'BTC/USDT' -> 'BTC/KRW'
        """
        base = binance_symbol.split('/')[0]
        return f"{base}/KRW"

    async def fetch_ticker(self, symbol: str) -> Dict:
        """
        특정 심볼의 티커 정보 조회

        Args:
            symbol: 거래 페어 (예: 'BTC/KRW')

        Returns:
            티커 정보 딕셔너리
        """
        try:
            ticker = await self.exchange.fetch_ticker(symbol)

            # 업비트는 ticker에 bid/ask가 없으므로 orderbook에서 가져옴
            bid = ticker.get('bid')
            ask = ticker.get('ask')

            if bid is None or ask is None:
                # orderbook에서 호가 정보 가져오기
                try:
                    orderbook = await self.exchange.fetch_order_book(symbol, limit=1)
                    if orderbook and 'bids' in orderbook and 'asks' in orderbook:
                        if orderbook['bids'] and len(orderbook['bids']) > 0:
                            bid = orderbook['bids'][0][0]  # 최우선 매수호가
                        if orderbook['asks'] and len(orderbook['asks']) > 0:
                            ask = orderbook['asks'][0][0]  # 최우선 매도호가
                except Exception as ob_error:
                    logger.warning(f"Could not fetch orderbook for {symbol}: {ob_error}")
                    # orderbook도 실패하면 last 가격 사용
                    bid = ticker.get('last')
                    ask = ticker.get('last')

            return {
                'symbol': symbol,
                'bid': bid,  # 매수 호가
                'ask': ask,  # 매도 호가
                'last': ticker['last'],  # 마지막 체결가
                'timestamp': ticker['timestamp'],
                'exchange': self.name
            }
        except Exception as e:
            logger.error(f"Error fetching {symbol} from Upbit: {e}")
            return None

    async def fetch_multiple_tickers(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        여러 심볼의 티커 정보를 한번에 조회

        Args:
            symbols: 거래 페어 리스트

        Returns:
            심볼별 티커 정보 딕셔너리
        """
        result = {}
        for symbol in symbols:
            upbit_symbol = self.convert_symbol(symbol)
            ticker = await self.fetch_ticker(upbit_symbol)
            if ticker:
                # 원래 심볼로 키를 설정하여 바이낸스와 매칭 가능하게
                result[symbol] = ticker
        return result

    def get_trading_fee(self, symbol: str = None) -> Dict[str, float]:
        """
        거래 수수료 조회

        Returns:
            maker, taker 수수료
        """
        # 업비트 기본 수수료
        return {
            'maker': 0.0005,  # 0.05%
            'taker': 0.0005   # 0.05%
        }

    async def close(self):
        """거래소 연결 종료"""
        await self.exchange.close()
