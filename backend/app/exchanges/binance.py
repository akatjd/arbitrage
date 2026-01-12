import ccxt.async_support as ccxt
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class BinanceExchange:
    """바이낸스 거래소 API 래퍼"""

    def __init__(self, api_key: str = None, secret: str = None):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            }
        })
        self.name = "Binance"

    async def fetch_ticker(self, symbol: str) -> Dict:
        """
        특정 심볼의 티커 정보 조회

        Args:
            symbol: 거래 페어 (예: 'BTC/USDT')

        Returns:
            티커 정보 딕셔너리
        """
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'bid': ticker['bid'],  # 매수 호가
                'ask': ticker['ask'],  # 매도 호가
                'last': ticker['last'],  # 마지막 체결가
                'timestamp': ticker['timestamp'],
                'exchange': self.name
            }
        except Exception as e:
            logger.error(f"Error fetching {symbol} from Binance: {e}")
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
            ticker = await self.fetch_ticker(symbol)
            if ticker:
                result[symbol] = ticker
        return result

    def get_trading_fee(self, symbol: str = None) -> Dict[str, float]:
        """
        거래 수수료 조회

        Returns:
            maker, taker 수수료
        """
        # 바이낸스 기본 수수료 (VIP 레벨에 따라 다를 수 있음)
        return {
            'maker': 0.001,  # 0.1%
            'taker': 0.001   # 0.1%
        }

    async def close(self):
        """거래소 연결 종료"""
        await self.exchange.close()
