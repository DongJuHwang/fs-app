#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
재무 데이터 처리 서비스
"""

from typing import Any, Dict, List, Optional, Tuple
from opendart_client import OpenDartClient
from utils import (
    create_user_friendly_error_message, 
    get_report_name,
    format_financial_data_for_display
)


class FinancialDataService:
    """재무 데이터 처리 서비스 클래스"""
    
    def __init__(self, opendart_client: OpenDartClient):
        self.opendart_client = opendart_client
    
    def get_financial_data(
        self, 
        corp_code: str, 
        year: str, 
        report_code: str
    ) -> Optional[List[Dict[str, Any]]]:
        """재무제표 데이터 가져오기"""
        try:
            print(f"🔍 재무제표 데이터 요청: corp_code={corp_code}, year={year}, report_code={report_code}")
            data = self.opendart_client.get_financial_info(corp_code, year, report_code)
            
            print(f"📊 API 응답: {type(data)}")
            if data:
                print(f"📋 응답 키: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if not data:
                print("❌ API 응답이 비어있습니다.")
                return None
            
            if 'list' not in data:
                print(f"❌ 'list' 키가 없습니다. 응답: {data}")
                return None
            
            if not data['list']:
                print("❌ 'list' 데이터가 비어있습니다.")
                return None
            
            print(f"✅ 재무제표 데이터 가져오기 성공: {len(data['list'])}개 항목")
            return data['list']
        except Exception as e:
            print(f"❌ 재무제표 데이터 가져오기 오류: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_financial_data_with_error_handling(
        self, 
        corp_code: str, 
        year: str, 
        report_code: str, 
        corp_name: str
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        """재무제표 데이터 가져오기 (에러 메시지 포함)"""
        try:
            data = self.opendart_client.get_financial_info(corp_code, year, report_code)
            
            if not data:
                error_msg = create_user_friendly_error_message(
                    corp_name, corp_code, year, report_code
                )
                return None, error_msg
            
            # API 오류 응답 처리 (status가 있는 경우)
            if isinstance(data, dict) and 'status' in data and data.get('status') != '000':
                status = data.get('status')
                message = data.get('message', '')
                
                error_msg = create_user_friendly_error_message(
                    corp_name, corp_code, year, report_code, status, message
                )
                return None, error_msg
            
            if 'list' not in data:
                return None, f"API 응답 형식 오류: {data}"
            
            if not data['list']:
                error_msg = create_user_friendly_error_message(
                    corp_name, corp_code, year, report_code
                )
                return None, error_msg
            
            return data['list'], None
        except Exception as e:
            return None, f"재무제표 데이터 가져오기 오류: {e}"
    
    def get_financial_data_range_with_error_handling(
        self, 
        corp_code: str, 
        start_year: str, 
        end_year: str, 
        report_code: str, 
        corp_name: str
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        """기간별 재무제표 데이터 가져오기 (에러 메시지 포함)"""
        try:
            data = self.opendart_client.get_financial_info_range(corp_code, start_year, end_year, report_code)
            
            if not data:
                error_msg = create_user_friendly_error_message(
                    corp_name, corp_code, f"{start_year}-{end_year}", report_code
                )
                return None, error_msg
            
            # API 오류 응답 처리 (status가 있는 경우)
            if isinstance(data, dict) and 'status' in data and data.get('status') != '000':
                status = data.get('status')
                message = data.get('message', '')
                
                error_msg = create_user_friendly_error_message(
                    corp_name, corp_code, f"{start_year}-{end_year}", report_code, status, message
                )
                return None, error_msg
            
            if 'list' not in data:
                return None, f"API 응답 형식 오류: {data}"
            
            if not data['list']:
                error_msg = create_user_friendly_error_message(
                    corp_name, corp_code, f"{start_year}-{end_year}", report_code
                )
                return None, error_msg
            
            return data['list'], None
        except Exception as e:
            return None, f"기간별 재무제표 데이터 가져오기 오류: {e}"
    
    def get_formatted_financial_data(
        self, 
        financial_data: List[Dict[str, Any]], 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """포맷팅된 재무 데이터 반환"""
        display_data = financial_data[:limit]
        return format_financial_data_for_display(display_data) 