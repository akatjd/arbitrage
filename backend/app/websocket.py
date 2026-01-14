from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Set
import asyncio
import logging
from datetime import datetime

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
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(connection)

        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


async def handle_funding_websocket(
    websocket: WebSocket,
    funding_service,
    symbols: List[str],
    update_interval: float = 5.0
):
    """
    펀딩 레이트 아비트리지 실시간 스트리밍

    Args:
        websocket: WebSocket 연결
        funding_service: FundingArbitrageService 인스턴스
        symbols: 모니터링할 심볼 리스트
        update_interval: 업데이트 주기 (초)
    """
    await manager.connect(websocket)

    try:
        logger.info(f"Starting funding rate stream for {len(symbols)} symbols")

        while True:
            try:
                # 모든 심볼에서 상위 아비트라지 기회 탐색
                all_opportunities = await funding_service.find_all_opportunities(
                    symbols=symbols,
                    default_position=10000,
                    default_leverage=2,
                    default_hours=24,
                    limit=20
                )

                # 클라이언트에게 전송
                message = {
                    'type': 'funding_update',
                    'data': [opp.dict() for opp in all_opportunities],
                    'total_opportunities': len(all_opportunities),
                    'timestamp': datetime.now().isoformat()
                }

                await manager.broadcast(message)
                logger.debug(f"Broadcast {len(all_opportunities)} opportunities")

            except Exception as e:
                logger.error(f"Error in funding stream: {e}")
                # 에러 발생 시 짧은 대기 후 재시도
                await asyncio.sleep(1)
                continue

            # 다음 업데이트까지 대기
            await asyncio.sleep(update_interval)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
