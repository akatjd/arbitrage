# Frontend - React Application

바이낸스와 업비트의 아비트라지 기회를 실시간으로 표시하는 React 웹 애플리케이션

## 기술 스택

- **React 18**: UI 라이브러리
- **Vite**: 빌드 도구 및 개발 서버
- **WebSocket**: 실시간 데이터 통신

## 디렉토리 구조

```
frontend/
├── src/
│   ├── components/          # React 컴포넌트
│   │   ├── Header.jsx       # 헤더 (연결 상태 표시)
│   │   ├── ArbitrageCard.jsx  # 아비트라지 카드
│   │   └── LoadingSpinner.jsx # 로딩 스피너
│   ├── hooks/               # 커스텀 React 훅
│   │   └── useWebSocket.js  # WebSocket 연결 관리
│   ├── App.jsx              # 메인 앱 컴포넌트
│   ├── App.css              # 앱 스타일
│   ├── main.jsx             # React 진입점
│   └── index.css            # 글로벌 스타일
├── index.html               # HTML 템플릿
├── package.json             # 의존성 및 스크립트
└── vite.config.js           # Vite 설정
```

## 설치 및 실행

### 1. 의존성 설치

```bash
npm install
```

### 2. 개발 서버 실행

```bash
npm run dev
```

브라우저가 자동으로 열리며 http://localhost:3000 에서 확인 가능합니다.

### 3. 프로덕션 빌드

```bash
npm run build
```

빌드된 파일은 `dist/` 디렉토리에 생성됩니다.

### 4. 빌드 미리보기

```bash
npm run preview
```

## 주요 기능

### 1. 실시간 데이터 표시
- WebSocket을 통한 1초 단위 실시간 업데이트
- 자동 재연결 기능
- 연결 상태 표시

### 2. 아비트라지 카드
- 수익률에 따른 색상 구분 (녹색: 수익, 빨간색: 손실)
- 양방향 거래 정보 표시
- 바이낸스/업비트 가격 비교
- 수수료 포함 매수/매도 가격

### 3. 통계 대시보드
- 전체 거래 페어 수
- 수익 가능한 기회 수
- 최고 수익률 표시
- 마지막 업데이트 시간

### 4. 반응형 디자인
- 모바일, 태블릿, 데스크톱 대응
- 그리드 레이아웃 자동 조정

## 컴포넌트 설명

### App.jsx
메인 애플리케이션 컴포넌트로 WebSocket 연결을 관리하고 전체 레이아웃을 구성합니다.

### Header.jsx
- 애플리케이션 제목 표시
- WebSocket 연결 상태 표시 (Connected/Disconnected)
- 상태에 따른 애니메이션 효과

### ArbitrageCard.jsx
개별 암호화폐의 아비트라지 정보를 카드 형태로 표시:
- 심볼 및 거래 방향
- 수익률
- 바이낸스/업비트 가격
- 환율 정보
- 매수/매도 가격

### LoadingSpinner.jsx
WebSocket 연결 중일 때 표시되는 로딩 인디케이터

### useWebSocket.js
WebSocket 연결을 관리하는 커스텀 훅:
- 자동 연결/재연결
- 메시지 수신 및 파싱
- 에러 처리
- 연결 상태 관리

## 환경 설정

### Backend URL 변경

[vite.config.js](vite.config.js)에서 백엔드 서버 주소를 변경할 수 있습니다:

```javascript
export default defineConfig({
  server: {
    proxy: {
      '/ws': {
        target: 'ws://your-backend-url:8000',
        ws: true,
      },
    },
  },
})
```

[src/App.jsx](src/App.jsx)에서 WebSocket URL을 변경할 수 있습니다:

```javascript
const { data, isConnected, error } = useWebSocket('ws://localhost:8000/ws');
```

## 스타일링

### 커스터마이징

- [src/index.css](src/index.css) - 글로벌 스타일 및 배경 그라디언트
- [src/App.css](src/App.css) - 앱 레벨 스타일 및 애니메이션
- 각 컴포넌트 - 인라인 스타일 객체

### 색상 테마 변경

컴포넌트 파일 내의 `styles` 객체를 수정하여 색상을 변경할 수 있습니다:

```javascript
const styles = {
  // 색상 커스터마이징
  primary: '#667eea',
  secondary: '#764ba2',
  success: '#10b981',
  danger: '#ef4444',
  // ...
};
```

## 문제 해결

### WebSocket 연결 오류
1. Backend 서버가 실행 중인지 확인
2. Backend URL이 올바른지 확인
3. CORS 설정 확인

### npm install 오류
```bash
# 캐시 정리 후 재설치
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### 빌드 오류
```bash
# 의존성 업데이트
npm update
npm run build
```

## 성능 최적화

- React.StrictMode 사용
- WebSocket 자동 재연결
- 효율적인 상태 관리
- CSS 애니메이션 사용

## 브라우저 지원

- Chrome (최신 버전)
- Firefox (최신 버전)
- Safari (최신 버전)
- Edge (최신 버전)
