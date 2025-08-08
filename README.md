# OpenDart API 프로젝트

OpenDart API를 사용하여 기업 정보를 조회하는 Python 프로젝트입니다.

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# OpenDart API Configuration
OPENDART_API_KEY=your_opendart_api_key_here

# Optional: API Base URL
OPENDART_BASE_URL=https://opendart.fss.or.kr/api
```

### 3. OpenDart API 키 발급
1. [OpenDart 웹사이트](https://opendart.fss.or.kr/)에 접속
2. 회원가입 후 로그인
3. "API 신청" 메뉴에서 API 키 발급
4. 발급받은 API 키를 `.env` 파일의 `OPENDART_API_KEY`에 입력

## 사용법

### 회사코드 파일 다운로드
```bash
# 전용 스크립트 실행
python download_corp_codes.py
```

### 기본 사용 예시
```python
from opendart_client import OpenDartClient

# 클라이언트 초기화
client = OpenDartClient()

# 기업코드 목록 조회
companies = client.get_corp_code_list()

# 특정 기업 정보 조회
company_info = client.get_company_info('corp_code_here')

# 재무정보 조회
financial_info = client.get_financial_info('corp_code_here', '2023', '11011')

# 회사코드 파일 다운로드 및 CSV 저장
df = client.get_corp_code_dataframe(save_csv=True)
print(f"총 {len(df)}개의 회사 정보를 다운로드했습니다.")

### 주요 메서드

- `get_corp_code_dataframe()`: 회사코드 파일 다운로드 및 DataFrame 반환
- `download_corp_code_file()`: 회사코드 ZIP 파일 다운로드
- `extract_corp_code_xml()`: ZIP 파일에서 XML 파일 추출
- `parse_corp_code_xml()`: XML 파일을 DataFrame으로 파싱
- `get_company_info(corp_code)`: 기업 기본정보 조회
- `get_financial_info(corp_code, year, report_code)`: 재무정보 조회
- `get_corp_code_list()`: 기업코드 목록 조회
- `search_company(company_name)`: 기업명으로 검색

## 파일 구조

```
├── .env                    # 환경 변수 파일 (직접 생성 필요)
├── config.py              # 설정 관리
├── opendart_client.py     # OpenDart API 클라이언트
├── download_corp_codes.py # 회사코드 다운로드 전용 스크립트
├── requirements.txt       # Python 의존성
├── README.md             # 프로젝트 설명서
└── data/                 # 다운로드된 데이터 파일들
    ├── corp_code.zip     # 원본 ZIP 파일
    ├── CORPCODE.xml      # 압축 해제된 XML 파일
    └── corp_code.csv     # 파싱된 회사 정보 CSV 파일
```

## 주의사항

- `.env` 파일은 절대 Git에 커밋하지 마세요
- API 키는 안전하게 보관하고 타인과 공유하지 마세요
- OpenDart API는 일일 호출 제한이 있으니 주의해서 사용하세요

## 문제 해결

### API 키 오류
- `.env` 파일이 프로젝트 루트에 있는지 확인
- API 키가 올바르게 입력되었는지 확인
- OpenDart 웹사이트에서 API 키 상태 확인

### 네트워크 오류
- 인터넷 연결 상태 확인
- 방화벽 설정 확인
- OpenDart 서버 상태 확인 