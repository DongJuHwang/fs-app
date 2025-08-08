#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
재무제표 시각화 웹 애플리케이션 (리팩토링 버전)
"""

import os
from typing import Any, Dict, List, Optional, Tuple
from flask import Flask, render_template, request, jsonify
from opendart_client import OpenDartClient
from data_service import FinancialDataService
from chart_service import ChartService
from utils import (
    convert_to_json_serializable,
    format_amount,
    load_corp_database,
    search_company
)


class FinancialDashboardApp:
    """재무 대시보드 애플리케이션 클래스"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.corp_database = {}
        self.opendart_client = None
        self.data_service = None
        self.chart_service = None
        
        # 템플릿 필터 등록
        self.app.template_filter('format_amount')(format_amount)
        
        # 라우트 등록
        self._register_routes()
    
    def initialize(self) -> bool:
        """애플리케이션 초기화"""
        # 데이터베이스 로드
        self.corp_database, success = load_corp_database()
        if not success:
            return False
        
        # OpenDart 클라이언트 초기화
        try:
            self.opendart_client = OpenDartClient()
            self.data_service = FinancialDataService(self.opendart_client)
            self.chart_service = ChartService()
            print("✅ OpenDart 클라이언트 초기화 완료")
            return True
        except Exception as e:
            print(f"❌ OpenDart 클라이언트 초기화 실패: {e}")
            return False
    
    def _register_routes(self):
        """라우트 등록"""
        
        @self.app.route('/')
        def index():
            """메인 페이지"""
            return render_template('index.html')
        
        @self.app.route('/test-chart')
        def test_chart():
            """차트 테스트 페이지"""
            return render_template('test_chart.html')
        
        @self.app.route('/search')
        def search():
            """회사 검색 API"""
            company_name = request.args.get('q', '')
            if not company_name:
                return jsonify([])
            
            results = search_company(company_name, self.corp_database)
            return jsonify(results)
        
        @self.app.route('/financial-api')
        def financial_api():
            """재무 데이터 API"""
            try:
                # 요청 파라미터 파싱
                corp_code = request.args.get('corp_code', '')
                corp_name = request.args.get('corp_name', '')
                view_mode = request.args.get('view_mode', 'single')
                
                if not corp_code:
                    return jsonify({'error': '회사코드가 필요합니다.'}), 400
                
                if view_mode == 'period':
                    # 기간별 조회
                    start_year = request.args.get('start_year', '')
                    end_year = request.args.get('end_year', '')
                    report_code = request.args.get('report_code', '11011')
                    
                    if not start_year or not end_year:
                        return jsonify({'error': '시작년도와 종료년도가 필요합니다.'}), 400
                    
                    financial_data, error_message = self.data_service.get_financial_data_range_with_error_handling(
                        corp_code, start_year, end_year, report_code, corp_name
                    )
                    
                    if not financial_data:
                        return jsonify({'error': error_message}), 404
                    
                    # 기간별 차트 생성
                    charts = self.chart_service.create_period_charts(financial_data)
                    
                else:
                    # 단일 연도 조회
                    year = request.args.get('year', '2022')
                    report_code = request.args.get('report_code', '11011')
                    
                    financial_data, error_message = self.data_service.get_financial_data_with_error_handling(
                        corp_code, year, report_code, corp_name
                    )
                    
                    if not financial_data:
                        return jsonify({'error': error_message}), 404
                    
                    # 단일 연도 차트 생성
                    print(f"📊 차트 생성 시작: 데이터 항목 수 {len(financial_data)}")
                    charts = self.chart_service.create_financial_charts(financial_data)
                    print(f"📈 생성된 차트 수: {len(charts) if charts else 0}")
                    if charts:
                        print(f"📋 차트 종류: {list(charts.keys())}")
                
                # JSON 직렬화 가능한 형태로 변환
                serializable_data = convert_to_json_serializable(financial_data)
                serializable_charts = convert_to_json_serializable(charts)
                
                return jsonify({
                    'success': True,
                    'data': serializable_data,
                    'charts': serializable_charts,
                    'corp_name': corp_name,
                    'corp_code': corp_code
                })
                
            except Exception as e:
                print(f"❌ API 오류: {e}")
                return jsonify({'error': f'서버 오류가 발생했습니다: {str(e)}'}), 500
        
        @self.app.route('/financial')
        def financial():
            """재무제표 페이지"""
            try:
                # 요청 파라미터 파싱
                corp_code = request.args.get('corp_code', '')
                corp_name = request.args.get('corp_name', '')
                year = request.args.get('year', '2022')
                start_year = request.args.get('start_year', '')
                end_year = request.args.get('end_year', '')
                report_code = request.args.get('report_code', '11011')
                view_mode = request.args.get('view_mode', 'single')
                
                if not corp_code:
                    return render_template('financial.html', error="회사코드가 필요합니다.")
                
                # 기간별 조회인지 단일 연도 조회인지 확인
                if view_mode == 'period' and start_year and end_year:
                    # 기간별 재무제표 데이터 가져오기
                    financial_data, error_message = self.data_service.get_financial_data_range_with_error_handling(
                        corp_code, start_year, end_year, report_code, corp_name
                    )
                    
                    if not financial_data:
                        return render_template('financial.html', 
                                             error=error_message,
                                             corp_name=corp_name,
                                             corp_code=corp_code,
                                             year=year,
                                             start_year=start_year,
                                             end_year=end_year,
                                             report_code=report_code,
                                             view_mode=view_mode,
                                             charts=None,
                                             financial_data=[])
                    
                    # 기간별 차트 생성
                    charts = self.chart_service.create_period_charts(financial_data)
                    display_data = self.data_service.get_formatted_financial_data(financial_data, 50)
                    
                else:
                    # 단일 연도 재무제표 데이터 가져오기
                    financial_data, error_message = self.data_service.get_financial_data_with_error_handling(
                        corp_code, year, report_code, corp_name
                    )
                    
                    if not financial_data:
                        return render_template('financial.html', 
                                             error=error_message,
                                             corp_name=corp_name,
                                             corp_code=corp_code,
                                             year=year,
                                             start_year=start_year,
                                             end_year=end_year,
                                             report_code=report_code,
                                             view_mode=view_mode,
                                             charts=None,
                                             financial_data=[])
                    
                    # 단일 연도 차트 생성
                    charts = self.chart_service.create_financial_charts(financial_data)
                    display_data = self.data_service.get_formatted_financial_data(financial_data, 20)
                
                # 기간별 분석 요약 정보 생성
                analysis_summary = None
                if view_mode == 'period' and financial_data:
                    analysis_summary = self._create_analysis_summary(financial_data, start_year, end_year)
                
                return render_template('financial.html', 
                                     corp_name=corp_name,
                                     corp_code=corp_code,
                                     year=year,
                                     start_year=start_year,
                                     end_year=end_year,
                                     report_code=report_code,
                                     view_mode=view_mode,
                                     charts=charts,
                                     financial_data=display_data,
                                     analysis_summary=analysis_summary)
                
            except Exception as e:
                print(f"❌ 페이지 오류: {e}")
                return render_template('financial.html', error=f"서버 오류가 발생했습니다: {str(e)}")
    
    def _create_analysis_summary(self, financial_data: List[Dict[str, Any]], start_year: str, end_year: str) -> Dict[str, Any]:
        """기간별 분석 요약 정보 생성"""
        try:
            # 데이터프레임 생성
            import pandas as pd
            df = pd.DataFrame(financial_data)
            
            # 연도별 데이터 그룹화
            year_data = {}
            for _, row in df.iterrows():
                year = row.get('bsns_year', '')
                if year not in year_data:
                    year_data[year] = {'BS': [], 'IS': []}
                
                fs_div = row.get('fs_div', '')
                if fs_div in ['BS', 'IS', 'CFS']:
                    # CFS 데이터는 BS와 IS 모두에 포함
                    if fs_div == 'CFS':
                        year_data[year]['BS'].append(row.to_dict())
                        year_data[year]['IS'].append(row.to_dict())
                    else:
                        year_data[year][fs_div].append(row.to_dict())
            
            # 요약 정보 생성
            summary = {
                'period': f"{start_year}년 ~ {end_year}년",
                'total_years': len(year_data),
                'years': sorted(year_data.keys()),
                'key_metrics': {}
            }
            
            # 주요 지표 추출
            for year in sorted(year_data.keys()):
                bs_data = year_data[year]['BS']
                is_data = year_data[year]['IS']
                
                if not bs_data or not is_data:
                    continue
                
                bs_dict = {item['account_nm']: item for item in bs_data}
                is_dict = {item['account_nm']: item for item in is_data}
                
                # 주요 지표 계산
                revenue = float(is_dict.get('매출액', {}).get('thstrm_amount', 0))
                net_income = float(is_dict.get('당기순이익', {}).get('thstrm_amount', 0))
                total_assets = float(bs_dict.get('자산총계', {}).get('thstrm_amount', 0))
                total_equity = float(bs_dict.get('자본총계', {}).get('thstrm_amount', 0))
                
                summary['key_metrics'][year] = {
                    'revenue': revenue,
                    'net_income': net_income,
                    'total_assets': total_assets,
                    'total_equity': total_equity,
                    'roe': (net_income / total_equity * 100) if total_equity > 0 else 0,
                    'roa': (net_income / total_assets * 100) if total_assets > 0 else 0
                }
            
            return summary
            
        except Exception as e:
            print(f"❌ 분석 요약 생성 오류: {e}")
            return None
    
    def run(self, debug: bool = True, host: str = '0.0.0.0', port: int = 8080):
        """애플리케이션 실행"""
        print("🚀 재무제표 시각화 웹 애플리케이션 시작...")
        print(f"   - URL: http://{host}:{port}")
        self.app.run(debug=debug, host=host, port=port)


def main():
    """메인 함수"""
    app = FinancialDashboardApp()
    
    # 애플리케이션 초기화
    if not app.initialize():
        print("❌ 애플리케이션을 시작할 수 없습니다.")
        return
    
    # 애플리케이션 실행
    app.run()

# Render 배포를 위한 애플리케이션 인스턴스
main_app = FinancialDashboardApp()
if main_app.initialize():
    app = main_app.app
else:
    raise RuntimeError("애플리케이션 초기화 실패")


if __name__ == '__main__':
    main() 