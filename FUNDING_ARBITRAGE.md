# Funding Rate Arbitrage Web Application

펀딩피(Funding Rate) 기반의 암호화폐 선물 아비트라지 기회를 실시간으로 모니터링하는 웹 애플리케이션입니다.

## 개요

이 애플리케이션은 여러 선물 거래소(Binance, Bybit, Lighter 등)의 펀딩 레이트를 실시간으로 추적하고, 거래소 간 펀딩 레이트 차이를 이용한 아비트라지 기회를 찾아줍니다.

## 주요 기능

### 1. 실시간 펀딩 레이트 모니터링
- 여러 거래소의 펀딩 레이트를 실시간으로 추적
- WebSocket을 통한 자동 업데이트 (60초마다)
- 지원 거래소: Binance Futures, Bybit Futures, Lighter

### 2. 아비트라지 기회 탐색
- 모든 심볼에 대해 거래소 간 펀딩 레이트 차이 계산
- APR(연 수익률) 자동 계산
- 상위 수익성 높은 기회 자동 정렬

### 3. 수익 계산기
- 포지션 크기, 레버리지, 보유 기간 입력
- 예상 수익, 필요 마진, 수익률 자동 계산
- Long/Short 거래소 조합 선택 가능

### 4. 직관적인 대시보드
- 실시간 연결 상태 표시
- 통계 요약 (총 기회 수, 수익성 기회, 최고 APR)
- 클릭 한 번으로 기회 선택 및 계산

## 실행 방법

### 백엔드 실행

```bash
cd backend
venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

백엔드가 `http://localhost:8000`에서 실행됩니다.

### 프론트엔드 실행

```bash
cd frontend
npm run dev
```

프론트엔드가 `http://localhost:3000`에서 실행됩니다.

### 브라우저에서 접속

`http://localhost:3000`을 브라우저에서 열면 펀딩피 아비트라지 대시보드를 확인할 수 있습니다.

## 화면 구성

### 1. 상단 헤더
- 애플리케이션 제목: "Funding Rate Arbitrage Monitor"
- 연결 상태 표시: Connected/Disconnected (실시간 WebSocket 연결 상태)

### 2. 통계 바
- **Connection Status**: LIVE (실시간 연결 상태)
- **Total Opportunities**: 발견된 총 아비트라지 기회 수
- **Profitable**: 수익성 있는 기회 수 (APR > 0)
- **Best APR**: 최고 연 수익률
- **Last Update**: 마지막 데이터 업데이트 시간

### 3. 펀딩 아비트라지 계산기
- **Trading Pair**: 거래 페어 선택 (BTC/USDT, ETH/USDT 등)
- **Long Exchange**: Long 포지션을 열 거래소
- **Short Exchange**: Short 포지션을 열 거래소
- **Position Size (USDT)**: 포지션 크기 (최소 100 USDT)
- **Leverage**: 레버리지 배수 (1~50배)
- **Holding Period (Hours)**: 보유 기간 (시간 단위)

계산 버튼 클릭 시 예상 수익이 계산됩니다.

### 4. 계산 결과 (결과가 있을 때만 표시)
- **APR**: 연 수익률
- **Funding Rate Spread**: 펀딩 레이트 차이
- **Price Spread**: 마크 가격 차이
- **Per Funding Profit**: 펀딩마다 발생하는 수익
- **Total Funding Count**: 총 펀딩 횟수
- **Estimated Total Profit**: 예상 총 수익 (USDT)
- **Profit Rate**: 수익률
- **Required Margin**: 필요한 마진
- **Position Size**: 포지션 크기

### 5. 상위 아비트라지 기회 (Top Opportunities)
- 수익성이 높은 상위 6개 기회 카드 형식으로 표시
- 각 카드 클릭 시 자동으로 계산기에 값이 입력되고 계산 실행
- 표시 정보:
  - 순위 (#1, #2, ...)
  - 심볼 (BTC, ETH 등)
  - APR (연 수익률)
  - Long/Short 거래소
  - Funding Spread (펀딩 레이트 차이)
  - 각 거래소의 펀딩 레이트

## API 엔드포인트

### REST API

- `GET /` - API 정보 및 엔드포인트 목록
- `GET /health` - 헬스 체크
- `GET /api/v1/exchanges` - 지원하는 거래소 목록
- `GET /api/v1/symbols` - 모니터링 중인 심볼 목록
- `GET /api/v1/funding-rates/{exchange}/{symbol}` - 특정 거래소의 펀딩 레이트
- `GET /api/v1/funding-rates/all/{symbol}` - 모든 거래소의 펀딩 레이트
- `POST /api/v1/funding-arbitrage/calculate` - 펀딩 아비트라지 계산
- `GET /api/v1/funding-arbitrage/top/{symbol}` - 심볼별 상위 기회
- `GET /api/v1/funding-arbitrage/all` - 모든 심볼의 상위 기회

### WebSocket

- `WS /ws` - 실시간 펀딩 레이트 아비트라지 데이터 스트리밍

메시지 형식:
```json
{
  "type": "funding_update",
  "data": [
    {
      "symbol": "BTC/USDT:USDT",
      "long_exchange": "binance",
      "short_exchange": "bybit",
      "long_funding_rate": 0.0001,
      "short_funding_rate": -0.0002,
      "funding_spread": 0.0003,
      "estimated_apr": 8.76,
      "rank": 1
    }
  ],
  "total_opportunities": 20,
  "timestamp": "2026-01-15T22:42:04.123456"
}
```

## 모니터링 심볼

현재 다음 심볼들을 모니터링합니다:
- BTC/USDT:USDT
- ETH/USDT:USDT
- SOL/USDT:USDT
- XRP/USDT:USDT
- DOGE/USDT:USDT
- AVAX/USDT:USDT
- LINK/USDT:USDT
- ARB/USDT:USDT
- OP/USDT:USDT

## 펀딩 레이트 아비트라지란?

암호화폐 선물 거래소는 무기한 선물(Perpetual Futures) 계약의 가격을 현물 가격에 가깝게 유지하기 위해 펀딩 레이트(Funding Rate) 메커니즘을 사용합니다.

- **양수 펀딩 레이트**: Long 포지션이 Short 포지션에게 수수료 지급
- **음수 펀딩 레이트**: Short 포지션이 Long 포지션에게 수수료 지급

거래소마다 펀딩 레이트가 다를 수 있으며, 이 차이를 이용하여:
- **펀딩 레이트가 낮은(또는 음수) 거래소**에서 Long 포지션 개설
- **펀딩 레이트가 높은(또는 양수) 거래소**에서 Short 포지션 개설
- 시장 방향성 리스크 없이 펀딩 레이트 차이만큼 수익 획득

## 주의사항

1. **실제 거래 전 충분한 테스트 필요**: 이 도구는 정보 제공 목적이며, 실제 거래 결정은 본인의 책임입니다.

2. **추가 비용 고려**:
   - 거래 수수료
   - 슬리피지
   - 출금/입금 수수료
   - 자금 이동 시간

3. **리스크 관리**:
   - 레버리지 사용 시 청산 위험
   - 거래소 간 가격 차이로 인한 손실 가능성
   - 펀딩 레이트 변동성

4. **API 키 보안**: 실제 거래를 위해 API 키를 사용할 경우 안전하게 관리

## 기술 스택

- **Backend**: FastAPI, ccxt, WebSocket, asyncio
- **Frontend**: React, Vite, WebSocket API
- **Data Source**: Binance Futures API, Bybit Futures API, Lighter API

## 문제 해결

### 백엔드가 시작되지 않는 경우
```bash
cd backend
pip install -r requirements.txt
```

### 프론트엔드가 시작되지 않는 경우
```bash
cd frontend
npm install
```

### WebSocket 연결이 안 되는 경우
- 백엔드가 실행 중인지 확인 (`http://localhost:8000/health`)
- 방화벽 설정 확인
- 브라우저 콘솔에서 에러 메시지 확인

## 라이선스

MIT License
