# 설치 및 실행 가이드

## 사전 요구사항

- Python 3.8 이상
- Node.js 18 이상
- Git

## 1. Backend 설정 및 실행

### 1.1 가상환경 생성 및 활성화

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 1.2 패키지 설치

```bash
pip install -r requirements.txt
```

### 1.3 환경 변수 설정 (선택사항)

공개 API만 사용하는 경우 이 단계를 건너뛰어도 됩니다.

```bash
# .env.example을 .env로 복사
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux

# .env 파일을 편집하여 API 키 입력 (선택사항)
```

### 1.4 서버 실행

```bash
# backend 디렉토리에서 실행
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 시작되면 다음 주소에서 접근 가능합니다:
- API: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 2. Frontend 설정 및 실행

### 2.1 새 터미널 열기

Backend 서버는 계속 실행된 상태로 두고, 새 터미널을 엽니다.

### 2.2 패키지 설치

```bash
cd frontend
npm install
```

### 2.3 개발 서버 실행

```bash
npm run dev
```

Frontend가 시작되면 브라우저에서 자동으로 열립니다:
- http://localhost:3000

## 3. 사용 방법

1. Backend와 Frontend가 모두 실행되면, 브라우저에서 자동으로 실시간 데이터가 표시됩니다.

2. 화면에 표시되는 정보:
   - **Symbol**: 암호화폐 심볼 (예: BTC, ETH)
   - **Direction**: 아비트라지 방향 (Binance → Upbit 또는 Upbit → Binance)
   - **Profit %**: 수수료 차감 후 예상 수익률
   - **Binance Price**: 바이낸스 가격 (USD 및 KRW)
   - **Upbit Price**: 업비트 가격 (KRW)
   - **Buy/Sell Price**: 수수료 포함 실제 매수/매도 가격

3. 카드 색상:
   - **녹색 경계선**: 수익성 있는 아비트라지 기회
   - **빨간색 경계선**: 수익성 없음

## 4. 환율 업데이트 (선택사항)

현재 환율을 업데이트하려면 API를 호출하세요:

```bash
curl -X POST "http://localhost:8000/exchange-rate?rate=1350"
```

## 5. 문제 해결

### Backend가 시작되지 않는 경우

```bash
# 패키지 재설치
pip install --upgrade -r requirements.txt

# 또는 특정 패키지 문제 해결
pip install --upgrade fastapi uvicorn ccxt
```

### Frontend가 시작되지 않는 경우

```bash
# node_modules 삭제 후 재설치
rm -rf node_modules
npm install

# 또는
npm cache clean --force
npm install
```

### WebSocket 연결 오류

1. Backend 서버가 실행 중인지 확인
2. 포트 8000이 사용 가능한지 확인
3. 방화벽 설정 확인

## 6. 프로덕션 빌드

### Frontend 빌드

```bash
cd frontend
npm run build
```

빌드된 파일은 `frontend/dist` 디렉토리에 생성됩니다.

### Backend 프로덕션 실행

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 7. 모니터링할 코인 변경

[backend/app/main.py](backend/app/main.py)의 `MONITORED_SYMBOLS` 리스트를 수정하세요:

```python
MONITORED_SYMBOLS = [
    'BTC/USDT',
    'ETH/USDT',
    'XRP/USDT',
    # 여기에 원하는 심볼 추가
]
```

## 8. 주의사항

- 이 도구는 정보 제공 목적입니다. 실제 거래 시 추가 비용(네트워크 수수료, 슬리피지 등)이 발생할 수 있습니다.
- 실시간 가격이므로 실제 체결가와 다를 수 있습니다.
- 거래소 API 키는 절대 공개하지 마세요.
