from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Set
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket 연결 관리"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """클라이언트 연결"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """클라이언트 연결 해제"""
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """모든 연결된 클라이언트에게 메시지 전송"""
        if not self.active_connections:
            return

        disconnected = set()
        # 복사본을 사용하여 순회 중 변경 방지
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}", exc_info=True)
                disconnected.add(connection)

        # 연결이 끊긴 클라이언트 제거
        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


async def handle_websocket(
    websocket: WebSocket,
    multi_exchange,
    arbitrage_calculator,
    exchange_rate_service,
    symbols: List[str],
    update_interval: float
):
    """
    WebSocket 연결 처리 및 실시간 데이터 전송

    Args:
        websocket: WebSocket 연결
        multi_exchange: 다중 거래소 인스턴스
        arbitrage_calculator: 다중 아비트라지 계산기
        exchange_rate_service: 환율 서비스
        symbols: 모니터링할 심볼 리스트
        update_interval: 업데이트 주기 (초)
    """
    await manager.connect(websocket)

    try:
        # 첫 실행 시 환율 업데이트
        exchange_rate = await exchange_rate_service.fetch_usd_krw_rate()
        arbitrage_calculator.update_exchange_rate(exchange_rate)

        update_count = 0

        while True:
            # 10번마다 환율 업데이트 (약 3분마다)
            if update_count % 10 == 0:
                exchange_rate = await exchange_rate_service.fetch_usd_krw_rate()
                arbitrage_calculator.update_exchange_rate(exchange_rate)

            update_count += 1

            all_opportunities = []
            logger.info(f"Starting data collection for {len(symbols)} symbols across multiple exchanges")

            # 각 심볼에 대해 아비트라지 계산
            for symbol in symbols:
                try:
                    # 모든 거래소에서 티커 조회
                    tickers = {}

                    # CEX 거래소들만 사용 (업비트 제외)
                    cex_tickers = await multi_exchange.fetch_all_tickers(symbol)
                    tickers.update(cex_tickers)

                    logger.debug(f"Fetched tickers for {symbol} from {len(tickers)} exchanges")

                    if len(tickers) >= 2:
                        # 수수료 정보 수집
                        fees = {}
                        for exchange_name in tickers.keys():
                            fees[exchange_name] = multi_exchange.get_trading_fee(exchange_name)

                        # 아비트라지 기회 계산
                        opportunities = arbitrage_calculator.calculate_arbitrage_opportunities(
                            tickers, fees
                        )

                        if opportunities:
                            all_opportunities.extend(opportunities)
                            logger.debug(f"Found {len(opportunities)} opportunities for {symbol}")

                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    continue

            # 수익률 순으로 정렬 (이미 계산기에서 정렬됨)
            all_opportunities.sort(
                key=lambda x: x['profit_percent'],
                reverse=True
            )

            # 상위 50개만 전송 (너무 많으면 UI 느려짐)
            top_opportunities = all_opportunities[:50]

            logger.info(f"Collected {len(all_opportunities)} total opportunities, sending top {len(top_opportunities)}")

            # 클라이언트에게 전송
            message = {
                'type': 'arbitrage_update',
                'data': top_opportunities,
                'exchange_rate': arbitrage_calculator.usd_to_krw_rate,
                'total_opportunities': len(all_opportunities),
                'timestamp': top_opportunities[0]['timestamp'] if top_opportunities else None
            }

            logger.info(f"Broadcasting message to {len(manager.active_connections)} clients")
            await manager.broadcast(message)
            logger.info("Broadcast complete")

            # 다음 업데이트까지 대기
            await asyncio.sleep(update_interval)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
