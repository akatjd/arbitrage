import ccxt.async_support as ccxt
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MultiExchange:
    """여러 거래소를 통합 관리하는 클래스"""

    def __init__(self, api_key: str = None, secret: str = None):
        self.exchanges = {}
        self.api_key = api_key
        self.secret = secret
        self._init_exchanges()

    def _init_exchanges(self):
        """지원하는 거래소 초기화"""
        exchange_configs = {
            'binance': {
                'class': ccxt.binance,
                'options': {'defaultType': 'spot'}
            },
            'coinbase': {
                'class': ccxt.coinbase,
                'options': {'defaultType': 'spot'}
            },
            'kraken': {
                'class': ccxt.kraken,
                'options': {}
            },
            'okx': {
                'class': ccxt.okx,
                'options': {'defaultType': 'spot'}
            },
            'bybit': {
                'class': ccxt.bybit,
                'options': {'defaultType': 'spot'}
            },
            'kucoin': {
                'class': ccxt.kucoin,
                'options': {'defaultType': 'spot'}
            },
            'gateio': {
                'class': ccxt.gateio,
                'options': {'defaultType': 'spot'}
            },
        }

        for name, config in exchange_configs.items():
            try:
                self.exchanges[name] = config['class']({
                    'apiKey': self.api_key,
                    'secret': self.secret,
                    'enableRateLimit': True,
                    'options': config['options']
                })
                logger.info(f"Initialized {name} exchange")
            except Exception as e:
                logger.warning(f"Failed to initialize {name}: {e}")

    async def fetch_ticker(self, exchange_name: str, symbol: str) -> Optional[Dict]:
        """
        특정 거래소의 티커 정보 조회

        Args:
            exchange_name: 거래소 이름
            symbol: 거래 페어 (예: 'BTC/USDT')

        Returns:
            티커 정보 딕셔너리
        """
        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not found")
            return None

        try:
            exchange = self.exchanges[exchange_name]
            ticker = await exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last'],
                'timestamp': ticker['timestamp'],
                'exchange': exchange_name.upper()
            }
        except Exception as e:
            logger.error(f"Error fetching {symbol} from {exchange_name}: {e}")
            return None

    async def fetch_all_tickers(self, symbol: str) -> Dict[str, Dict]:
        """
        모든 거래소에서 특정 심볼의 티커 정보 조회

        Args:
            symbol: 거래 페어

        Returns:
            거래소별 티커 정보
        """
        result = {}
        for exchange_name in self.exchanges.keys():
            ticker = await self.fetch_ticker(exchange_name, symbol)
            if ticker:
                result[exchange_name] = ticker
        return result

    def get_trading_fee(self, exchange_name: str) -> Dict[str, float]:
        """
        거래소별 수수료 반환

        Args:
            exchange_name: 거래소 이름

        Returns:
            maker, taker 수수료
        """
        fees = {
            'binance': {'maker': 0.001, 'taker': 0.001},  # 0.1%
            'coinbase': {'maker': 0.004, 'taker': 0.006},  # 0.4% / 0.6%
            'kraken': {'maker': 0.0016, 'taker': 0.0026},  # 0.16% / 0.26%
            'okx': {'maker': 0.0008, 'taker': 0.001},  # 0.08% / 0.1%
            'bybit': {'maker': 0.001, 'taker': 0.001},  # 0.1%
            'kucoin': {'maker': 0.001, 'taker': 0.001},  # 0.1%
            'gateio': {'maker': 0.002, 'taker': 0.002},  # 0.2%
            'upbit': {'maker': 0.0005, 'taker': 0.0005},  # 0.05%
        }
        return fees.get(exchange_name, {'maker': 0.002, 'taker': 0.002})

    async def close(self):
        """모든 거래소 연결 종료"""
        for exchange in self.exchanges.values():
            try:
                await exchange.close()
            except Exception as e:
                logger.error(f"Error closing exchange: {e}")
