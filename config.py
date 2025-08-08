import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """OpenDart API 설정 클래스"""
    
    # OpenDart API 키
    OPENDART_API_KEY = os.getenv('OPENDART_API_KEY')
    
    # OpenDart API 기본 URL
    OPENDART_BASE_URL = os.getenv('OPENDART_BASE_URL', 'https://opendart.fss.or.kr/api')
    
    @classmethod
    def validate_config(cls):
        """설정 유효성 검사"""
        if not cls.OPENDART_API_KEY:
            raise ValueError("OPENDART_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        return True 