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
    binance_exchange,
    upbit_exchange,
    arbitrage_calculator,
    symbols: List[str],
    update_interval: float
):
    """
    WebSocket 연결 처리 및 실시간 데이터 전송

    Args:
        websocket: WebSocket 연결
        binance_exchange: 바이낸스 거래소 인스턴스
        upbit_exchange: 업비트 거래소 인스턴스
        arbitrage_calculator: 아비트라지 계산기
        symbols: 모니터링할 심볼 리스트
        update_interval: 업데이트 주기 (초)
    """
    await manager.connect(websocket)

    try:
        while True:
            arbitrage_opportunities = []
            logger.info(f"Starting data collection for {len(symbols)} symbols")

            # 각 심볼에 대해 아비트라지 계산
            for symbol in symbols:
                try:
                    # 바이낸스 티커 조회
                    binance_ticker = await binance_exchange.fetch_ticker(symbol)
                    logger.debug(f"Fetched Binance ticker for {symbol}: {binance_ticker is not None}")

                    # 업비트 티커 조회
                    upbit_ticker = await upbit_exchange.fetch_ticker(
                        upbit_exchange.convert_symbol(symbol)
                    )
                    logger.debug(f"Fetched Upbit ticker for {symbol}: {upbit_ticker is not None}")

                    if binance_ticker and upbit_ticker:
                        # 아비트라지 계산
                        arbitrage = arbitrage_calculator.calculate_arbitrage(
                            binance_ticker,
                            upbit_ticker,
                            binance_exchange.get_trading_fee(),
                            upbit_exchange.get_trading_fee()
                        )

                        if arbitrage:
                            arbitrage_opportunities.append(arbitrage)

                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    continue

            # 평균 김치 프리미엄 계산
            avg_premium = 0
            if arbitrage_opportunities:
                total_premium = sum(opp['raw_premium_percent'] for opp in arbitrage_opportunities)
                avg_premium = total_premium / len(arbitrage_opportunities)

                # 각 코인에 순수 차익 추가 (김치 프리미엄 제외)
                for opp in arbitrage_opportunities:
                    opp['pure_arbitrage_percent'] = round(opp['raw_premium_percent'] - avg_premium, 4)

            # 수익률 순으로 정렬
            arbitrage_opportunities.sort(
                key=lambda x: x['profit_percent'],
                reverse=True
            )

            logger.info(f"Collected {len(arbitrage_opportunities)} arbitrage opportunities (Avg premium: {avg_premium:.2f}%)")

            # 클라이언트에게 전송
            message = {
                'type': 'arbitrage_update',
                'data': arbitrage_opportunities,
                'avg_kimchi_premium': round(avg_premium, 4),
                'timestamp': arbitrage_opportunities[0]['timestamp'] if arbitrage_opportunities else None
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
