import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ExchangeRateService:
    """실시간 환율 조회 서비스"""

    def __init__(self):
        self.current_rate = 1300  # 기본값
        self.last_update = None

    async def fetch_usd_krw_rate(self) -> Optional[float]:
        """
        실시간 USD/KRW 환율 조회

        Returns:
            USD/KRW 환율
        """
        try:
            # exchangerate-api.com 사용 (무료, API 키 불필요)
            async with aiohttp.ClientSession() as session:
                url = "https://open.er-api.com/v6/latest/USD"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        krw_rate = data['rates'].get('KRW')
                        if krw_rate:
                            self.current_rate = krw_rate
                            logger.info(f"Exchange rate updated: 1 USD = {krw_rate} KRW")
                            return krw_rate
        except Exception as e:
            logger.error(f"Error fetching exchange rate: {e}")

        # 실패 시 기존 환율 반환
        return self.current_rate

    def get_current_rate(self) -> float:
        """현재 환율 반환"""
        return self.current_rate
