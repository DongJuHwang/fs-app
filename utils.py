#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
재무 대시보드 유틸리티 함수들
"""

import json
import os
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union


def convert_to_json_serializable(obj: Any) -> Any:
    """객체를 JSON 직렬화 가능한 형태로 변환"""
    if isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif hasattr(obj, 'item'):  # pandas/numpy scalar types
        return obj.item()
    else:
        return obj


def format_amount(amount_str: Union[str, int, float]) -> str:
    """금액을 직관적인 단위로 포맷팅"""
    try:
        if not amount_str or amount_str == '-':
            return '0'
        
        # 문자열로 변환 후 콤마 제거
        amount_str = str(amount_str)
        amount = int(amount_str.replace(',', ''))
        
        if abs(amount) >= 1000000000000:  # 1조 이상
            return f"{amount / 1000000000000:.1f}조"
        elif abs(amount) >= 100000000:  # 1억 이상
            return f"{amount / 100000000:.1f}억"
        elif abs(amount) >= 10000:  # 1만 이상
            return f"{amount / 10000:.1f}만"
        else:
            return f"{amount:,}"
    except (ValueError, AttributeError):
        return str(amount_str)


def safe_convert(value: Any) -> float:
    """안전한 숫자 변환"""
    try:
        if isinstance(value, str):
            # 콤마 제거 후 변환
            return float(value.replace(',', ''))
        elif isinstance(value, (int, float)):
            return float(value)
        else:
            return 0.0
    except (ValueError, TypeError):
        return 0.0


def get_report_name(report_code: str) -> str:
    """보고서 코드를 보고서 이름으로 변환"""
    report_names = {
        '11011': '사업보고서',
        '11012': '반기보고서', 
        '11013': '1분기보고서',
        '11014': '3분기보고서'
    }
    return report_names.get(report_code, report_code)


def create_user_friendly_error_message(
    corp_name: str, 
    corp_code: str, 
    year: str, 
    report_code: str,
    status: Optional[str] = None,
    message: Optional[str] = None
) -> str:
    """사용자 친화적인 오류 메시지 생성"""
    report_name = get_report_name(report_code)
    
    if status == '013' and message and '조회된 데이타가 없습니다' in message:
        return f"📊 {corp_name}({corp_code})의 {year}년 {report_name} 데이터를 찾을 수 없습니다.\n\n💡 다른 연도나 보고서 유형을 선택해보세요."
    else:
        return f"📊 {corp_name}({corp_code})의 {year}년 {report_name} 데이터 조회 중 오류가 발생했습니다.\n\n💡 다른 연도나 보고서 유형을 선택해보세요."


def load_corp_database() -> Tuple[Dict[str, Any], bool]:
    """회사코드 데이터베이스 로드"""
    json_path = os.path.join("data", "corpCodes.json")
    
    if not os.path.exists(json_path):
        print("❌ corpCodes.json 파일이 없습니다. 먼저 데이터베이스를 생성해주세요.")
        return {}, False
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            corp_database = json.load(f)
        print(f"✅ 회사코드 데이터베이스 로드 완료: {len(corp_database):,}개 회사")
        return corp_database, True
    except Exception as e:
        print(f"❌ 데이터베이스 로드 오류: {e}")
        return {}, False


def search_company(company_name: str, corp_database: Dict[str, Any]) -> List[Dict[str, str]]:
    """회사명으로 검색"""
    if not company_name or not corp_database:
        return []
    
    results = []
    company_name_lower = company_name.lower()
    
    for corp_name, corp_info in corp_database.items():
        if company_name_lower in corp_name.lower():
            results.append({
                'corp_name': corp_name,
                'corp_code': corp_info['corp_code'],
                'stock_code': corp_info['stock_code']
            })
    
    return results[:10]  # 상위 10개만 반환


def format_financial_data_for_display(financial_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """재무 데이터에 포맷팅된 금액 필드 추가"""
    formatted_data = []
    
    for item in financial_data:
        formatted_item = item.copy()
        formatted_item['thstrm_amount_formatted'] = format_amount(item.get('thstrm_amount', '0'))
        formatted_item['frmtrm_amount_formatted'] = format_amount(item.get('frmtrm_amount', '0'))
        
        if 'bfefrmtrm_amount' in item:
            formatted_item['bfefrmtrm_amount_formatted'] = format_amount(item.get('bfefrmtrm_amount', '0'))
        
        formatted_data.append(formatted_item)
    
    return formatted_data 