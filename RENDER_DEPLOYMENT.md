# Render 배포 가이드 (리팩토링 버전)

## 🚀 Render 배포 준비 완료!

리팩토링이 완료된 재무 대시보드를 Render에 배포하는 방법을 안내합니다.

## 📋 사전 준비사항

1. **GitHub 계정** - 코드 저장소용
2. **Render 계정** - [https://render.com](https://render.com)에서 생성
3. **OpenDart API 키** - [https://opendart.fss.or.kr](https://opendart.fss.or.kr)에서 발급

## 🔧 배포 단계

### 1단계: GitHub에 코드 푸시

```bash
# Git 저장소 초기화 (아직 안 했다면)
git init
git add .
git commit -m "Refactored financial dashboard for Render deployment"

# GitHub 저장소 생성 후 연결
git remote add origin https://github.com/yourusername/financial-dashboard.git
git push -u origin main
```

### 2단계: Render에서 새 Web Service 생성

1. **Render 대시보드 접속**
   - [https://dashboard.render.com](https://dashboard.render.com) 접속
   - 로그인 후 "New +" 버튼 클릭

2. **Web Service 선택**
   - "Web Service" 선택
   - "Connect a repository" 클릭

3. **GitHub 저장소 연결**
   - GitHub 계정 연결 (아직 안 했다면)
   - `financial-dashboard` 저장소 선택

### 3단계: 서비스 설정

다음 설정을 입력하세요:

- **Name**: `financial-dashboard`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### 4단계: 환경 변수 설정

**Environment Variables** 섹션에서 다음 변수들을 추가:

| Key | Value | 설명 |
|-----|-------|------|
| `OPENDART_API_KEY` | `your_api_key_here` | OpenDart API 키 (필수) |
| `OPENDART_BASE_URL` | `https://opendart.fss.or.kr/api` | API 기본 URL |
| `PYTHON_VERSION` | `3.11.7` | Python 버전 |

### 5단계: 배포 시작

"Create Web Service" 버튼을 클릭하여 배포를 시작합니다.

## 📊 배포 상태 확인

### 빌드 로그 확인
- Render 대시보드에서 서비스 선택
- "Logs" 탭에서 빌드 및 실행 로그 확인

### 성공적인 배포 확인 사항
```
✅ Build successful
✅ Dependencies installed
✅ Application started
✅ Health check passed
```

## 🌐 배포 완료 후

### 1. 서비스 URL 확인
- Render 대시보드에서 제공되는 URL 확인
- 예: `https://financial-dashboard.onrender.com`

### 2. 기능 테스트
다음 URL들로 기능 테스트:

- **메인 페이지**: `https://your-app.onrender.com/`
- **재무 페이지**: `https://your-app.onrender.com/financial?corp_code=00126380&corp_name=삼성전자`
- **API 테스트**: `https://your-app.onrender.com/financial-api?corp_code=00126380&corp_name=삼성전자&year=2023`

## 🔧 문제 해결

### 일반적인 문제들

#### 1. 빌드 실패
```
❌ Build failed: ModuleNotFoundError
```
**해결책**: `requirements.txt`에 모든 의존성이 포함되어 있는지 확인

#### 2. 애플리케이션 시작 실패
```
❌ Application failed to start
```
**해결책**: 
- 환경 변수 `OPENDART_API_KEY`가 설정되었는지 확인
- `data/corpCodes.json` 파일이 존재하는지 확인

#### 3. API 오류
```
❌ OpenDart API 오류
```
**해결책**:
- API 키가 유효한지 확인
- OpenDart 서비스 상태 확인

### 로그 확인 방법
```bash
# Render 대시보드에서 실시간 로그 확인
# 또는 curl로 헬스체크
curl https://your-app.onrender.com/
```

## 📈 성능 최적화

### Render 무료 티어 제한사항
- **월 사용량**: 750시간
- **메모리**: 512MB
- **CPU**: 0.1 CPU
- **스토리지**: 1GB

### 최적화 팁
1. **이미지 캐싱**: Plotly 차트 이미지 캐싱 활용
2. **데이터베이스**: 필요시 PostgreSQL 추가 (유료)
3. **CDN**: 정적 파일 CDN 활용

## 🔄 업데이트 배포

코드 변경 후 자동 배포:
```bash
git add .
git commit -m "Update: 새로운 기능 추가"
git push origin main
```

Render가 자동으로 새 배포를 시작합니다.

## 📞 지원

문제가 발생하면:
1. Render 로그 확인
2. GitHub Issues 생성
3. OpenDart API 상태 확인

## 🎉 배포 완료!

배포가 완료되면 다음과 같은 기능들을 사용할 수 있습니다:

- ✅ **회사 검색**: 실시간 회사명 검색
- ✅ **재무제표 조회**: 단일 연도 및 기간별 조회
- ✅ **차트 시각화**: 재무상태표, 손익계산서, 재무비율 차트
- ✅ **API 서비스**: RESTful API 제공
- ✅ **반응형 UI**: 모바일/데스크톱 지원

**배포 URL**: `https://your-app.onrender.com` 