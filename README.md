# Crypto Arbitrage Monitor

바이낸스와 업비트 간의 암호화폐 아비트라지 기회를 실시간으로 모니터링하는 웹 애플리케이션

## 기술 스택

### Backend
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **WebSocket**: 실시간 가격 업데이트
- **ccxt**: 통합 거래소 API 라이브러리
- **python-dotenv**: 환경 변수 관리

### Frontend
- **React**: UI 라이브러리
- **Vite**: 빠른 개발 서버 및 빌드 도구
- **WebSocket**: 실시간 데이터 수신

## 주요 기능

- ✅ 실시간 가격 모니터링 (바이낸스 & 업비트)
- ✅ 아비트라지 기회 자동 계산
- ✅ 거래 수수료 포함 실제 수익률 계산
- ✅ 직관적인 웹 인터페이스

## 프로젝트 구조

```
arbitrage/
├── backend/          # FastAPI 서버
│   ├── app/
│   │   ├── main.py           # FastAPI 앱 진입점
│   │   ├── websocket.py      # WebSocket 핸들러
│   │   ├── exchanges/        # 거래소 API 래퍼
│   │   └── services/         # 아비트라지 계산 로직
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/         # React 앱
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   └── hooks/
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## 빠른 시작

자세한 설치 및 실행 가이드는 [SETUP.md](SETUP.md)를 참조하세요.

### Backend 실행

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

자세한 내용: [backend/README.md](backend/README.md)

### Frontend 실행

```bash
cd frontend
npm install
npm run dev
```

자세한 내용: [frontend/README.md](frontend/README.md)

## 문서

- [SETUP.md](SETUP.md) - 상세 설치 및 실행 가이드
- [backend/README.md](backend/README.md) - Backend API 문서
- [frontend/README.md](frontend/README.md) - Frontend 개발 가이드

## 라이선스

MIT
