from fastapi import FastAPI, WebSocket, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from app.config import settings
from app.models.funding import (
    FundingArbitrageRequest,
    FundingArbitrageResult,
    TopArbitrageOpportunity,
    ExchangeType
)
from app.exchanges.futures_manager import FuturesManager
from app.services.funding_arbitrage import FundingArbitrageService
from app.websocket import handle_funding_websocket

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 모니터링할 심볼 리스트 (무기한 선물)
MONITORED_SYMBOLS = [
    'BTC/USDT:USDT',
    'ETH/USDT:USDT',
    'SOL/USDT:USDT',
    'XRP/USDT:USDT',
    'DOGE/USDT:USDT',
    'AVAX/USDT:USDT',
    'LINK/USDT:USDT',
    'ARB/USDT:USDT',
    'OP/USDT:USDT',
]

# 전역 인스턴스
futures_manager: Optional[FuturesManager] = None
funding_service: Optional[FundingArbitrageService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    global futures_manager, funding_service

    # 시작 시 초기화
    logger.info("Initializing Funding Rate Arbitrage services...")

    config = {
        'binance_api_key': settings.binance_api_key,
        'binance_secret': settings.binance_secret_key,
    }

    futures_manager = FuturesManager(config)
    await futures_manager.initialize()

    funding_service = FundingArbitrageService(futures_manager)

    logger.info("Services initialized successfully")

    yield

    # 종료 시 정리
    logger.info("Shutting down...")
    if futures_manager:
        await futures_manager.close_all()


# FastAPI 앱 생성
app = FastAPI(
    title="Funding Rate Arbitrage API",
    description="선물 거래소 간 펀딩 레이트 아비트리지 모니터링 API",
    version="2.0.0",
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
        "message": "Funding Rate Arbitrage API",
        "version": "2.0.0",
        "endpoints": {
            "websocket": "/ws",
            "health": "/health",
            "exchanges": "/api/v1/exchanges",
            "symbols": "/api/v1/symbols",
            "funding_rates": "/api/v1/funding-rates/{exchange}/{symbol}",
            "calculate": "/api/v1/funding-arbitrage/calculate",
            "top_opportunities": "/api/v1/funding-arbitrage/top/{symbol}"
        }
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "exchanges": futures_manager.get_available_exchanges() if futures_manager else [],
        "exchange_count": len(futures_manager.exchanges) if futures_manager else 0
    }


@app.get("/api/v1/exchanges")
async def get_exchanges():
    """지원하는 거래소 목록"""
    if not futures_manager:
        raise HTTPException(status_code=503, detail="Service not initialized")

    return {
        "exchanges": futures_manager.get_exchange_info()
    }


@app.get("/api/v1/symbols")
async def get_symbols():
    """모니터링 중인 심볼 목록"""
    return {
        "symbols": MONITORED_SYMBOLS,
        "count": len(MONITORED_SYMBOLS)
    }


@app.get("/api/v1/funding-rates/{exchange}/{symbol:path}")
async def get_funding_rate(exchange: str, symbol: str):
    """특정 거래소의 펀딩 레이트 조회"""
    if not futures_manager:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        exchange_type = ExchangeType(exchange.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid exchange: {exchange}")

    rate = await futures_manager.get_funding_rate(exchange_type, symbol)

    if not rate:
        raise HTTPException(status_code=404, detail="Funding rate not found")

    return rate


@app.get("/api/v1/funding-rates/all/{symbol:path}")
async def get_all_funding_rates(symbol: str):
    """모든 거래소의 펀딩 레이트 조회"""
    if not futures_manager:
        raise HTTPException(status_code=503, detail="Service not initialized")

    rates = await futures_manager.get_all_funding_rates(symbol)

    return {
        "symbol": symbol,
        "rates": {k.value: v.dict() for k, v in rates.items()},
        "exchange_count": len(rates)
    }


@app.post("/api/v1/funding-arbitrage/calculate")
async def calculate_funding_arbitrage(request: FundingArbitrageRequest):
    """펀딩 아비트리지 계산"""
    if not futures_manager or not funding_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    long_rate = await futures_manager.get_funding_rate(
        request.long_exchange, request.symbol
    )
    short_rate = await futures_manager.get_funding_rate(
        request.short_exchange, request.symbol
    )

    if not long_rate:
        raise HTTPException(
            status_code=404,
            detail=f"Funding rate not available for {request.long_exchange.value}"
        )

    if not short_rate:
        raise HTTPException(
            status_code=404,
            detail=f"Funding rate not available for {request.short_exchange.value}"
        )

    result = funding_service.calculate_arbitrage(request, long_rate, short_rate)
    return result


@app.get("/api/v1/funding-arbitrage/top/{symbol:path}")
async def get_top_opportunities(
    symbol: str,
    position_size: float = Query(10000, description="Position size in USDT"),
    leverage: float = Query(2, description="Leverage multiplier"),
    holding_hours: int = Query(24, description="Holding period in hours")
):
    """상위 아비트리지 기회 조회"""
    if not funding_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    opportunities = await funding_service.find_top_opportunities(
        symbol=symbol,
        default_position=position_size,
        default_leverage=leverage,
        default_hours=holding_hours
    )

    return {
        "symbol": symbol,
        "opportunities": [opp.dict() for opp in opportunities],
        "count": len(opportunities)
    }


@app.get("/api/v1/funding-arbitrage/all")
async def get_all_top_opportunities(
    position_size: float = Query(10000, description="Position size in USDT"),
    leverage: float = Query(2, description="Leverage multiplier"),
    holding_hours: int = Query(24, description="Holding period in hours"),
    limit: int = Query(20, description="Maximum number of results")
):
    """모든 심볼에서 상위 아비트리지 기회 조회"""
    if not funding_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    opportunities = await funding_service.find_all_opportunities(
        symbols=MONITORED_SYMBOLS,
        default_position=position_size,
        default_leverage=leverage,
        default_hours=holding_hours,
        limit=limit
    )

    return {
        "opportunities": [opp.dict() for opp in opportunities],
        "count": len(opportunities)
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 엔드포인트
    실시간 펀딩 레이트 아비트리지 데이터 스트리밍
    """
    await handle_funding_websocket(
        websocket=websocket,
        funding_service=funding_service,
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
