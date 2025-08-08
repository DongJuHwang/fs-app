import requests
import pandas as pd
import zipfile
import xml.etree.ElementTree as ET
import os
from config import Config

class OpenDartClient:
    """OpenDart API 클라이언트"""
    
    def __init__(self):
        """초기화 및 설정 검증"""
        Config.validate_config()
        self.api_key = Config.OPENDART_API_KEY
        self.base_url = Config.OPENDART_BASE_URL
        
        # data 폴더 생성
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _make_request(self, endpoint, params=None, is_binary=False):
        """API 요청 수행"""
        url = f"{self.base_url}/{endpoint}"
        
        # 기본 파라미터에 API 키 추가
        if params is None:
            params = {}
        params['crtfc_key'] = self.api_key
        
        print(f"🌐 요청 URL: {url}")
        print(f"🔑 API 키: {self.api_key[:10]}...")
        
        try:
            response = requests.get(url, params=params)
            print(f"📡 HTTP 상태 코드: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ HTTP 오류: {response.status_code}")
                print(f"📄 응답 내용: {response.text[:500]}")
                return None
            
            if is_binary:
                return response.content
            else:
                json_data = response.json()
                print(f"✅ JSON 응답 타입: {type(json_data)}")
                if isinstance(json_data, dict):
                    print(f"📋 응답 키: {list(json_data.keys())}")
                return json_data
        except requests.exceptions.RequestException as e:
            print(f"❌ API 요청 오류: {e}")
            return None
        except ValueError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            print(f"📄 응답 내용: {response.text[:500]}")
            return None
    
    def download_corp_code_file(self, save_path=None):
        """회사코드 파일 다운로드 (ZIP 파일)"""
        if save_path is None:
            save_path = os.path.join(self.data_dir, "corp_code.zip")
        
        print("회사코드 파일 다운로드 중...")
        zip_content = self._make_request('corpCode.xml', is_binary=True)
        
        if zip_content:
            # ZIP 파일 저장
            with open(save_path, 'wb') as f:
                f.write(zip_content)
            print(f"회사코드 파일이 {save_path}에 저장되었습니다.")
            return save_path
        else:
            print("회사코드 파일 다운로드에 실패했습니다.")
            return None
    
    def extract_corp_code_xml(self, zip_path=None, extract_path=None):
        """ZIP 파일에서 XML 파일 추출"""
        if zip_path is None:
            zip_path = os.path.join(self.data_dir, "corp_code.zip")
        if extract_path is None:
            extract_path = self.data_dir
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # ZIP 파일 내의 파일 목록 확인
                file_list = zip_ref.namelist()
                print(f"ZIP 파일 내 파일 목록: {file_list}")
                
                # XML 파일 추출
                for file_name in file_list:
                    if file_name.endswith('.xml'):
                        zip_ref.extract(file_name, extract_path)
                        xml_path = os.path.join(extract_path, file_name)
                        print(f"XML 파일이 {xml_path}에 추출되었습니다.")
                        return xml_path
            
            print("ZIP 파일에서 XML 파일을 찾을 수 없습니다.")
            return None
        except zipfile.BadZipFile:
            print("잘못된 ZIP 파일입니다.")
            return None
        except Exception as e:
            print(f"ZIP 파일 추출 중 오류 발생: {e}")
            return None
    
    def parse_corp_code_xml(self, xml_path):
        """XML 파일을 파싱하여 회사 정보를 DataFrame으로 변환"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            companies = []
            for company in root.findall('.//list'):
                company_info = {
                    'corp_code': company.find('corp_code').text if company.find('corp_code') is not None else '',
                    'corp_name': company.find('corp_name').text if company.find('corp_name') is not None else '',
                    'corp_eng_name': company.find('corp_eng_name').text if company.find('corp_eng_name') is not None else '',
                    'stock_code': company.find('stock_code').text if company.find('stock_code') is not None else '',
                    'modify_date': company.find('modify_date').text if company.find('modify_date') is not None else ''
                }
                companies.append(company_info)
            
            df = pd.DataFrame(companies)
            print(f"총 {len(df)}개의 회사 정보를 파싱했습니다.")
            return df
            
        except ET.ParseError as e:
            print(f"XML 파싱 오류: {e}")
            return None
        except Exception as e:
            print(f"파싱 중 오류 발생: {e}")
            return None
    
    def get_corp_code_dataframe(self, save_csv=True, csv_path=None):
        """회사코드 파일을 다운로드하고 DataFrame으로 반환"""
        if csv_path is None:
            csv_path = os.path.join(self.data_dir, "corp_code.csv")
        
        # 1. ZIP 파일 다운로드
        zip_path = self.download_corp_code_file()
        if not zip_path:
            return None
        
        # 2. XML 파일 추출
        xml_path = self.extract_corp_code_xml(zip_path)
        if not xml_path:
            return None
        
        # 3. XML 파일 파싱
        df = self.parse_corp_code_xml(xml_path)
        if df is not None and save_csv:
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"회사 정보가 {csv_path}에 저장되었습니다.")
        
        return df
    
    def get_company_info(self, corp_code):
        """기업 기본정보 조회"""
        corp_code = str(corp_code).zfill(8)  # 8자리로 패딩
        return self._make_request('company.json', {'corp_code': corp_code})
    
    def get_financial_info(self, corp_code, year, report_code):
        """재무정보 조회"""
        # OpenDart API 공식 문서에 따른 파라미터
        corp_code = str(corp_code).zfill(8)  # 8자리로 패딩
        params = {
            'corp_code': corp_code,
            'bsns_year': year,
            'reprt_code': report_code
        }
        print(f"🔗 API 요청 URL: {self.base_url}/fnlttSinglAcnt.json")
        print(f"📝 요청 파라미터: {params}")
        return self._make_request('fnlttSinglAcnt.json', params)
    
    def get_financial_info_range(self, corp_code, start_year, end_year, report_code):
        """기간별 재무정보 조회"""
        corp_code = str(corp_code).zfill(8)  # 8자리로 패딩
        all_data = []
        successful_years = []
        
        for year in range(int(start_year), int(end_year) + 1):
            print(f"📅 {year}년 데이터 조회 중...")
            try:
                data = self.get_financial_info(corp_code, str(year), report_code)
                
                # API 오류 응답 처리 (status가 있는 경우)
                if isinstance(data, dict) and 'status' in data and data.get('status') != '000':
                    status = data.get('status')
                    message = data.get('message', '')
                    if status == '013' and '조회된 데이타가 없습니다' in message:
                        print(f"⚠️ {year}년 데이터 없음 (API 응답: {message})")
                    else:
                        print(f"❌ {year}년 데이터 조회 실패 (API 응답: {message})")
                    continue
                
                if data and isinstance(data, dict) and 'list' in data and data['list']:
                    # 연도 정보를 각 항목에 추가
                    for item in data['list']:
                        item['query_year'] = str(year)
                        item['bsns_year'] = str(year)  # 명시적으로 사업연도 추가
                    all_data.extend(data['list'])
                    successful_years.append(year)
                    print(f"✅ {year}년 데이터 조회 완료 ({len(data['list'])}개 항목)")
                else:
                    print(f"⚠️ {year}년 데이터 없음")
            except Exception as e:
                print(f"❌ {year}년 데이터 조회 실패: {e}")
        
        if all_data:
            print(f"🎯 총 {len(successful_years)}개 연도 데이터 취합 완료: {successful_years}")
            return {'list': all_data, 'years': successful_years}
        else:
            print("⚠️ 조회된 기간 데이터가 없습니다.")
            return None
    
    def get_corp_code_list(self):
        """기업코드 목록 조회"""
        return self._make_request('corpCode.xml')
    
    def search_company(self, company_name):
        """기업명으로 검색"""
        return self._make_request('company.json', {'corp_name': company_name})

# 사용 예시
if __name__ == "__main__":
    client = OpenDartClient()
    
    # 회사코드 파일 다운로드 및 DataFrame으로 변환
    print("=== 회사코드 파일 다운로드 및 파싱 ===")
    df = client.get_corp_code_dataframe()
    
    if df is not None:
        print("\n=== 상위 10개 회사 정보 ===")
        print(df.head(10))
        
        print(f"\n=== 전체 회사 수: {len(df)}개 ===")
        
        # 상장회사만 필터링 (종목코드가 있는 회사)
        listed_companies = df[df['stock_code'].notna() & (df['stock_code'] != '')]
        print(f"상장회사 수: {len(listed_companies)}개")
        
        print("\n=== 상장회사 상위 10개 ===")
        print(listed_companies.head(10)) 