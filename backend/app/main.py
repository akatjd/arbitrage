from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.exchanges.multi_exchange import MultiExchange
from app.services.multi_arbitrage import MultiArbitrageCalculator
from app.services.exchange_rate import ExchangeRateService
from app.websocket import handle_websocket

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 모니터링할 심볼 리스트 (USDT 페어)
# 업비트에 상장된 코인만 포함
MONITORED_SYMBOLS = [
    'BTC/USDT',
    'ETH/USDT',
    'XRP/USDT',
    'SOL/USDT',
    'ADA/USDT',
    'AVAX/USDT',
    'DOGE/USDT',
    'DOT/USDT',
    'LINK/USDT',
]

# 전역 인스턴스
multi_exchange = None
arbitrage_calculator = None
exchange_rate_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    global multi_exchange, arbitrage_calculator, exchange_rate_service

    # 시작 시 초기화
    logger.info("Initializing exchanges and services...")
    multi_exchange = MultiExchange(
        api_key=settings.binance_api_key,
        secret=settings.binance_secret_key
    )
    exchange_rate_service = ExchangeRateService()

    # 초기 환율 가져오기
    initial_rate = await exchange_rate_service.fetch_usd_krw_rate()
    arbitrage_calculator = MultiArbitrageCalculator(usd_to_krw_rate=initial_rate)

    logger.info(f"Services initialized successfully (Exchange rate: {initial_rate} KRW/USD)")

    yield

    # 종료 시 정리
    logger.info("Shutting down...")
    if multi_exchange:
        await multi_exchange.close()


# FastAPI 앱 생성
app = FastAPI(
    title="Crypto Arbitrage API",
    description="바이낸스와 업비트 간의 암호화폐 아비트라지 모니터링 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Crypto Arbitrage API",
        "version": "1.0.0",
        "endpoints": {
            "websocket": "/ws",
            "health": "/health",
            "symbols": "/symbols"
        }
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "exchanges": {
            "multi_exchange": multi_exchange is not None
        },
        "exchange_rate": arbitrage_calculator.usd_to_krw_rate if arbitrage_calculator else None
    }


@app.get("/symbols")
async def get_symbols():
    """모니터링 중인 심볼 목록 조회"""
    return {
        "symbols": MONITORED_SYMBOLS,
        "count": len(MONITORED_SYMBOLS)
    }


@app.post("/exchange-rate")
async def update_exchange_rate(rate: float):
    """
    USD/KRW 환율 업데이트

    Args:
        rate: 새로운 환율
    """
    if arbitrage_calculator:
        arbitrage_calculator.update_exchange_rate(rate)
        return {"message": "Exchange rate updated", "rate": rate}
    return {"error": "Arbitrage calculator not initialized"}, 500


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 엔드포인트
    실시간 아비트라지 데이터 스트리밍
    """
    await handle_websocket(
        websocket=websocket,
        multi_exchange=multi_exchange,
        arbitrage_calculator=arbitrage_calculator,
        exchange_rate_service=exchange_rate_service,
        symbols=MONITORED_SYMBOLS,
        update_interval=settings.price_update_interval
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
