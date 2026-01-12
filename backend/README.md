# Backend - FastAPI Server

바이낸스와 업비트의 가격 데이터를 수집하고 아비트라지 기회를 계산하는 FastAPI 백엔드 서버

## 기술 스택

- **FastAPI**: 고성능 비동기 웹 프레임워크
- **WebSocket**: 실시간 데이터 스트리밍
- **ccxt**: 통합 거래소 API 라이브러리
- **Uvicorn**: ASGI 서버

## 디렉토리 구조

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 애플리케이션 진입점
│   ├── config.py            # 환경 변수 및 설정
│   ├── websocket.py         # WebSocket 연결 관리
│   ├── exchanges/           # 거래소 API 래퍼
│   │   ├── __init__.py
│   │   ├── binance.py       # 바이낸스 API
│   │   └── upbit.py         # 업비트 API
│   └── services/            # 비즈니스 로직
│       ├── __init__.py
│       └── arbitrage.py     # 아비트라지 계산
├── requirements.txt         # Python 의존성
└── .env.example            # 환경 변수 예시
```

## 설치 및 실행

### 1. 가상환경 생성

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정 (선택사항)

```bash
# .env.example을 .env로 복사
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux
```

공개 API만 사용하는 경우 API 키 없이도 실행 가능합니다.

### 4. 서버 실행

```bash
# 개발 모드 (자동 재시작)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 모드
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 엔드포인트

### HTTP 엔드포인트

- `GET /` - API 정보
- `GET /health` - 헬스 체크
- `GET /symbols` - 모니터링 중인 심볼 목록
- `POST /exchange-rate?rate={rate}` - USD/KRW 환율 업데이트

### WebSocket 엔드포인트

- `WS /ws` - 실시간 아비트라지 데이터 스트리밍

## API 문서

서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 모니터링 심볼 변경

[app/main.py](app/main.py)의 `MONITORED_SYMBOLS` 리스트를 수정하세요:

```python
MONITORED_SYMBOLS = [
    'BTC/USDT',
    'ETH/USDT',
    # 원하는 심볼 추가
]
```

## 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `BINANCE_API_KEY` | 바이낸스 API 키 (선택) | None |
| `BINANCE_SECRET_KEY` | 바이낸스 시크릿 키 (선택) | None |
| `UPBIT_ACCESS_KEY` | 업비트 액세스 키 (선택) | None |
| `UPBIT_SECRET_KEY` | 업비트 시크릿 키 (선택) | None |
| `HOST` | 서버 호스트 | 0.0.0.0 |
| `PORT` | 서버 포트 | 8000 |
| `PRICE_UPDATE_INTERVAL` | 가격 업데이트 주기 (초) | 1.0 |

## 주요 기능

### 1. 거래소 API 래퍼
- 바이낸스와 업비트의 실시간 가격 조회
- 심볼 형식 자동 변환 (BTC/USDT ↔ BTC/KRW)
- 거래 수수료 정보 제공

### 2. 아비트라지 계산
- 양방향 수익률 계산 (Binance→Upbit, Upbit→Binance)
- 거래 수수료 자동 반영
- 송금 수수료 포함
- USD/KRW 환율 적용

### 3. 실시간 데이터 스트리밍
- WebSocket을 통한 실시간 업데이트
- 다중 클라이언트 지원
- 자동 재연결 처리

## 문제 해결

### 패키지 설치 오류
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### 포트 충돌
```bash
# 다른 포트로 실행
uvicorn app.main:app --port 8001
```

### ccxt 관련 오류
```bash
pip install --upgrade ccxt aiohttp
```
