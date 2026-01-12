# 프로젝트 구조

## 전체 디렉토리 구조

```
arbitrage/
│
├── backend/                    # FastAPI 백엔드 서버
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 애플리케이션 진입점
│   │   ├── config.py          # 환경 변수 및 설정 관리
│   │   ├── websocket.py       # WebSocket 연결 및 실시간 데이터 브로드캐스트
│   │   │
│   │   ├── exchanges/         # 거래소 API 래퍼
│   │   │   ├── __init__.py
│   │   │   ├── binance.py     # 바이낸스 API 통합
│   │   │   └── upbit.py       # 업비트 API 통합
│   │   │
│   │   └── services/          # 비즈니스 로직
│   │       ├── __init__.py
│   │       └── arbitrage.py   # 아비트라지 계산 서비스
│   │
│   ├── requirements.txt       # Python 의존성
│   ├── .env.example          # 환경 변수 예시
│   └── README.md             # Backend 문서
│
├── frontend/                  # React 프론트엔드 앱
│   ├── src/
│   │   ├── components/        # React 컴포넌트
│   │   │   ├── Header.jsx     # 헤더 및 연결 상태
│   │   │   ├── ArbitrageCard.jsx  # 아비트라지 정보 카드
│   │   │   └── LoadingSpinner.jsx # 로딩 인디케이터
│   │   │
│   │   ├── hooks/             # 커스텀 React 훅
│   │   │   └── useWebSocket.js    # WebSocket 연결 관리
│   │   │
│   │   ├── App.jsx            # 메인 애플리케이션 컴포넌트
│   │   ├── App.css            # 앱 스타일
│   │   ├── main.jsx           # React 진입점
│   │   └── index.css          # 글로벌 스타일
│   │
│   ├── index.html             # HTML 템플릿
│   ├── package.json           # Node.js 의존성
│   ├── vite.config.js         # Vite 빌드 설정
│   └── README.md              # Frontend 문서
│
├── .gitignore                 # Git 제외 파일 목록
├── README.md                  # 프로젝트 개요
├── SETUP.md                   # 상세 설치 가이드
└── PROJECT_STRUCTURE.md       # 이 문서

```

## 주요 파일 설명

### Backend

| 파일 | 설명 |
|------|------|
| `backend/app/main.py` | FastAPI 애플리케이션 진입점, API 엔드포인트 정의 |
| `backend/app/config.py` | 환경 변수 및 애플리케이션 설정 |
| `backend/app/websocket.py` | WebSocket 연결 관리 및 실시간 데이터 브로드캐스트 |
| `backend/app/exchanges/binance.py` | 바이낸스 API 래퍼 (티커 조회, 수수료) |
| `backend/app/exchanges/upbit.py` | 업비트 API 래퍼 (티커 조회, 수수료) |
| `backend/app/services/arbitrage.py` | 아비트라지 수익률 계산 로직 |
| `backend/requirements.txt` | Python 패키지 의존성 목록 |

### Frontend

| 파일 | 설명 |
|------|------|
| `frontend/src/App.jsx` | 메인 애플리케이션, WebSocket 데이터 처리 |
| `frontend/src/components/Header.jsx` | 헤더 컴포넌트 (제목, 연결 상태) |
| `frontend/src/components/ArbitrageCard.jsx` | 개별 아비트라지 기회 표시 카드 |
| `frontend/src/components/LoadingSpinner.jsx` | 로딩 상태 표시 |
| `frontend/src/hooks/useWebSocket.js` | WebSocket 연결 관리 커스텀 훅 |
| `frontend/src/index.css` | 글로벌 스타일 (배경, 폰트) |
| `frontend/src/App.css` | 앱 레벨 스타일 및 애니메이션 |
| `frontend/vite.config.js` | Vite 개발 서버 및 빌드 설정 |
| `frontend/package.json` | Node.js 패키지 의존성 목록 |

## 데이터 흐름

```
┌─────────────┐         ┌─────────────┐
│   Binance   │         │   Upbit     │
│     API     │         │     API     │
└──────┬──────┘         └──────┬──────┘
       │                       │
       │ fetch prices          │ fetch prices
       │                       │
       └───────────┬───────────┘
                   ↓
         ┌─────────────────────┐
         │  Backend (FastAPI)  │
         │  ─────────────────  │
         │  • Exchange APIs    │
         │  • Arbitrage Calc   │
         │  • WebSocket Server │
         └─────────┬───────────┘
                   │
                   │ WebSocket
                   │ (real-time data)
                   ↓
         ┌─────────────────────┐
         │  Frontend (React)   │
         │  ─────────────────  │
         │  • Display Cards    │
         │  • Statistics       │
         │  • Connection UI    │
         └─────────────────────┘
                   │
                   ↓
              User Browser
```

## 기술 스택 요약

### Backend
- **FastAPI**: 비동기 웹 프레임워크
- **ccxt**: 거래소 API 통합 라이브러리
- **WebSocket**: 실시간 양방향 통신
- **Uvicorn**: ASGI 서버
- **Pydantic**: 데이터 검증 및 설정 관리

### Frontend
- **React 18**: 선언적 UI 라이브러리
- **Vite**: 빠른 개발 환경 및 빌드 도구
- **WebSocket API**: 실시간 데이터 수신
- **CSS-in-JS**: 컴포넌트 스타일링

## 개발 워크플로우

### 1. 새로운 거래소 추가
1. `backend/app/exchanges/` 에 새 거래소 클래스 생성
2. `fetch_ticker()` 및 `get_trading_fee()` 메서드 구현
3. `backend/app/main.py` 에서 거래소 인스턴스 생성
4. WebSocket 핸들러에 추가

### 2. 새로운 UI 컴포넌트 추가
1. `frontend/src/components/` 에 새 컴포넌트 파일 생성
2. `App.jsx` 에서 임포트 및 사용
3. 필요한 스타일 추가

### 3. 새로운 API 엔드포인트 추가
1. `backend/app/main.py` 에 새 라우트 정의
2. 필요한 경우 `services/` 에 비즈니스 로직 추가
3. Frontend에서 API 호출 구현

## 환경별 설정

### 개발 환경
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- WebSocket: `ws://localhost:8000/ws`

### 프로덕션 환경
- Backend: 별도 서버 배포 (Uvicorn + Nginx)
- Frontend: 정적 파일로 빌드 후 배포
- CORS 설정 업데이트 필요

## 의존성 관리

### Backend
```bash
# 의존성 추가
pip install <package-name>
pip freeze > requirements.txt

# 의존성 설치
pip install -r requirements.txt
```

### Frontend
```bash
# 의존성 추가
npm install <package-name>

# 의존성 설치
npm install
```

## 참고 문서

- [README.md](README.md) - 프로젝트 개요
- [SETUP.md](SETUP.md) - 상세 설치 가이드
- [backend/README.md](backend/README.md) - Backend API 문서
- [frontend/README.md](frontend/README.md) - Frontend 개발 가이드
