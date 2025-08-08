#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
차트 생성 서비스
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Any, Dict, List, Optional, Tuple
from utils import format_amount, safe_convert


class ChartService:
    """차트 생성 서비스 클래스"""
    
    def __init__(self):
        self.chart_config = {
            'modebar': dict(remove=[
                'pan', 'select', 'lasso2d', 'autoScale2d', 
                'hoverClosestCartesian', 'hoverCompareCartesian', 'toggleSpikelines'
            ]),
            'paper_bgcolor': '#004060',
            'plot_bgcolor': '#004060',
            'font': dict(color='#e0e0e0')
        }
    
    def create_balance_sheet_chart(self, bs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """재무상태표 차트 생성 - 막대그래프 + 텍스트 테이블"""
        if not bs_data:
            return {}
        
        # 주요 계정과목만 필터링 및 중복 제거
        key_accounts = ['자산총계', '부채총계', '자본총계']
        filtered_data = [item for item in bs_data if item.get('account_nm') in key_accounts]
        
        if not filtered_data:
            return {}
        
        # 중복 제거 - 계정명 기준으로 첫 번째 항목만 사용
        unique_data = {}
        for item in filtered_data:
            account_name = item.get('account_nm', '')
            if account_name not in unique_data:
                unique_data[account_name] = item
        
        # 데이터 준비
        account_names = []
        current_amounts = []
        previous_amounts = []
        
        for account_name in key_accounts:
            if account_name in unique_data:
                item = unique_data[account_name]
                account_names.append(account_name)
                current_amounts.append(safe_convert(item.get('thstrm_amount', 0)))
                previous_amounts.append(safe_convert(item.get('frmtrm_amount', 0)))
        
        # 막대그래프 생성
        fig = go.Figure()
        
        # 조 단위로 변환
        current_amounts_cho = [amount / 1000000000000 for amount in current_amounts]
        previous_amounts_cho = [amount / 1000000000000 for amount in previous_amounts]
        
        # Y축 범위 계산
        all_amounts = current_amounts_cho + previous_amounts_cho
        max_amount = max(all_amounts) if all_amounts else 100
        min_amount = min(all_amounts) if all_amounts else 0
        
        # Y축 틱 값 생성 (조 단위) - 100 단위로 깔끔하게
        max_val = int(max_amount)
        if max_val <= 100:
            tick_vals = [0, 25, 50, 75, 100]
        elif max_val <= 200:
            tick_vals = [0, 50, 100, 150, 200]
        elif max_val <= 500:
            tick_vals = [0, 100, 200, 300, 400, 500]
        elif max_val <= 1000:
            tick_vals = [0, 200, 400, 600, 800, 1000]
        else:
            tick_vals = [0, 500, 1000, 1500, 2000]
        
        tick_texts = [f"{val}조" for val in tick_vals]
        
        fig.add_trace(go.Bar(
            name='당기',
            x=account_names,
            y=current_amounts_cho,
            marker_color='rgb(55, 83, 109)',
            hovertemplate='<b>%{x}</b><br>당기: %{text}<extra></extra>',
            text=[format_amount(str(int(amount))) for amount in current_amounts],
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='전기',
            x=account_names,
            y=previous_amounts_cho,
            marker_color='rgb(26, 118, 255)',
            hovertemplate='<b>%{x}</b><br>전기: %{text}<extra></extra>',
            text=[format_amount(str(int(amount))) for amount in previous_amounts],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='재무상태표',
            xaxis_title='',
            yaxis_title='',
            barmode='group',
            height=450,
            margin=dict(l=50, r=50, t=80, b=80),
            yaxis=dict(
                tickformat='.0f',
                tickmode='array',
                ticktext=tick_texts,
                tickvals=tick_vals
            ),
            **self.chart_config
        )
        
        # 텍스트 테이블 생성
        table_fig = go.Figure(data=[go.Table(
            header=dict(
                values=['', '당기', '전기', '증감'],
                fill_color='#002040',
                font=dict(color='#e0e0e0', size=12),
                align='center'
            ),
            cells=dict(
                values=[
                    account_names,
                    [format_amount(str(int(amount))) for amount in current_amounts],
                    [format_amount(str(int(amount))) for amount in previous_amounts],
                    [format_amount(str(int(current - previous))) for current, previous in zip(current_amounts, previous_amounts)]
                ],
                fill_color='#004060',
                font=dict(color='#e0e0e0', size=10),
                align='center',
                height=30
            )
        )])
        
        table_fig.update_layout(
            title='',
            height=150,
            margin=dict(l=10, r=10, t=20, b=10),
            **self.chart_config
        )
        
        return {
            'balance_sheet': fig.to_html(full_html=False, include_plotlyjs=False),
            'balance_sheet_table': table_fig.to_html(full_html=False, include_plotlyjs=False)
        }
    
    def create_income_statement_chart(self, is_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """손익계산서 차트 생성 - 막대그래프 + 텍스트 테이블"""
        if not is_data:
            return {}
        
        # 주요 계정과목만 필터링 및 중복 제거
        key_accounts = ['매출액', '영업이익', '당기순이익']
        filtered_data = [item for item in is_data if item.get('account_nm') in key_accounts]
        
        if not filtered_data:
            return {}
        
        # 중복 제거 - 계정명 기준으로 첫 번째 항목만 사용
        unique_data = {}
        for item in filtered_data:
            account_name = item.get('account_nm', '')
            if account_name not in unique_data:
                unique_data[account_name] = item
        
        # 데이터 준비
        account_names = []
        current_amounts = []
        previous_amounts = []
        
        for account_name in key_accounts:
            if account_name in unique_data:
                item = unique_data[account_name]
                account_names.append(account_name)
                current_amounts.append(safe_convert(item.get('thstrm_amount', 0)))
                previous_amounts.append(safe_convert(item.get('frmtrm_amount', 0)))
        
        # 막대그래프 생성
        fig = go.Figure()
        
        # 조 단위로 변환
        current_amounts_cho = [amount / 1000000000000 for amount in current_amounts]
        previous_amounts_cho = [amount / 1000000000000 for amount in previous_amounts]
        
        # Y축 범위 계산
        all_amounts = current_amounts_cho + previous_amounts_cho
        max_amount = max(all_amounts) if all_amounts else 100
        min_amount = min(all_amounts) if all_amounts else 0
        
        # Y축 틱 값 생성 (조 단위) - 100 단위로 깔끔하게
        max_val = int(max_amount)
        if max_val <= 100:
            tick_vals = [0, 25, 50, 75, 100]
        elif max_val <= 200:
            tick_vals = [0, 50, 100, 150, 200]
        elif max_val <= 500:
            tick_vals = [0, 100, 200, 300, 400, 500]
        elif max_val <= 1000:
            tick_vals = [0, 200, 400, 600, 800, 1000]
        else:
            tick_vals = [0, 500, 1000, 1500, 2000]
        
        tick_texts = [f"{val}조" for val in tick_vals]
        
        fig.add_trace(go.Bar(
            name='당기',
            x=account_names,
            y=current_amounts_cho,
            marker_color='rgb(158, 202, 225)',
            hovertemplate='<b>%{x}</b><br>당기: %{text}<extra></extra>',
            text=[format_amount(str(int(amount))) for amount in current_amounts],
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='전기',
            x=account_names,
            y=previous_amounts_cho,
            marker_color='rgb(94, 158, 217)',
            hovertemplate='<b>%{x}</b><br>전기: %{text}<extra></extra>',
            text=[format_amount(str(int(amount))) for amount in previous_amounts],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='손익계산서',
            xaxis_title='',
            yaxis_title='',
            barmode='group',
            height=450,
            margin=dict(l=50, r=50, t=80, b=80),
            yaxis=dict(
                tickformat='.0f',
                tickmode='array',
                ticktext=tick_texts,
                tickvals=tick_vals
            ),
            **self.chart_config
        )
        
        # 텍스트 테이블 생성
        table_fig = go.Figure(data=[go.Table(
            header=dict(
                values=['', '당기', '전기', '증감'],
                fill_color='#002040',
                font=dict(color='#e0e0e0', size=12),
                align='center'
            ),
            cells=dict(
                values=[
                    account_names,
                    [format_amount(str(int(amount))) for amount in current_amounts],
                    [format_amount(str(int(amount))) for amount in previous_amounts],
                    [format_amount(str(int(current - previous))) for current, previous in zip(current_amounts, previous_amounts)]
                ],
                fill_color='#004060',
                font=dict(color='#e0e0e0', size=10),
                align='center',
                height=30
            )
        )])
        
        table_fig.update_layout(
            title='',
            height=150,
            margin=dict(l=10, r=10, t=20, b=10),
            **self.chart_config
        )
        
        return {
            'income_statement': fig.to_html(full_html=False, include_plotlyjs=False),
            'income_statement_table': table_fig.to_html(full_html=False, include_plotlyjs=False)
        }
    
    def create_profitability_radar_chart(
        self, 
        bs_data: List[Dict[str, Any]], 
        is_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """수익성 분석 레이더 차트 생성"""
        if not bs_data or not is_data:
            return {}
        
        # 데이터 준비
        bs_dict = {item['account_nm']: item for item in bs_data}
        is_dict = {item['account_nm']: item for item in is_data}
        
        # 재무비율 계산
        ratios = []
        ratio_names = []
        account_names = []
        numerator_amounts = []
        base_amounts = []
        
        # ROE (당기순이익 / 자본총계)
        net_income = safe_convert(is_dict.get('당기순이익', {}).get('thstrm_amount', 0))
        total_equity = safe_convert(bs_dict.get('자본총계', {}).get('thstrm_amount', 0))
        if total_equity > 0:
            roe = (net_income / total_equity) * 100
            ratios.append(roe)
            ratio_names.append('ROE<br>(자기자본이익률)')
            account_names.append('당기순이익 / 자본총계')
            numerator_amounts.append(format_amount(str(int(net_income))))
            base_amounts.append(format_amount(str(int(total_equity))))
        
        # ROA (당기순이익 / 자산총계)
        total_assets = safe_convert(bs_dict.get('자산총계', {}).get('thstrm_amount', 0))
        if total_assets > 0:
            roa = (net_income / total_assets) * 100
            ratios.append(roa)
            ratio_names.append('ROA<br>(총자산이익률)')
            account_names.append('당기순이익 / 자산총계')
            numerator_amounts.append(format_amount(str(int(net_income))))
            base_amounts.append(format_amount(str(int(total_assets))))
        
        # 영업이익률 (영업이익 / 매출액)
        operating_income = safe_convert(is_dict.get('영업이익', {}).get('thstrm_amount', 0))
        revenue = safe_convert(is_dict.get('매출액', {}).get('thstrm_amount', 0))
        if revenue > 0:
            operating_margin = (operating_income / revenue) * 100
            ratios.append(operating_margin)
            ratio_names.append('영업이익률')
            account_names.append('영업이익 / 매출액')
            numerator_amounts.append(format_amount(str(int(operating_income))))
            base_amounts.append(format_amount(str(int(revenue))))
        
        # 순이익률 (당기순이익 / 매출액)
        if revenue > 0:
            net_margin = (net_income / revenue) * 100
            ratios.append(net_margin)
            ratio_names.append('순이익률')
            account_names.append('당기순이익 / 매출액')
            numerator_amounts.append(format_amount(str(int(net_income))))
            base_amounts.append(format_amount(str(int(revenue))))
        
        if not ratios:
            return {}
        
        # 레이더 차트 생성
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=ratios,
            theta=ratio_names,
            fill='toself',
            name='수익성 비율',
            line_color='rgb(32, 201, 151)',
            mode='lines+markers+text',
            text=[f'{ratio:.2f}%' for ratio in ratios],
            textposition='middle center',
            hovertemplate='<b>%{theta}</b><br>비율: %{r:.2f}%<br><br><b>계산 공식:</b><br>%{customdata[0]}<br><br><b>분자 (당기순이익/영업이익):</b> %{customdata[1]}<br><b>분모 (자본총계/자산총계/매출액):</b> %{customdata[2]}<extra></extra>',
            customdata=list(zip(account_names, numerator_amounts, base_amounts))
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, max(ratios) * 1.2],
                    showgrid=False
                ),
                bgcolor='#004060'
            ),
            showlegend=False,
            title='수익성 분석',
            height=550,
            margin=dict(l=50, r=50, t=80, b=50),
            **self.chart_config
        )
        
        return {'profitability_radar': fig.to_html(full_html=False, include_plotlyjs=False)}
    
    def create_combined_financial_ratios_chart(
        self, 
        bs_data: List[Dict[str, Any]], 
        is_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """통합 재무비율 차트 생성"""
        charts = {}
        
        # 수익성 레이더 차트
        profitability_chart = self.create_profitability_radar_chart(bs_data, is_data)
        charts.update(profitability_chart)
        
        # 부채비율 도넛 차트
        debt_chart = self.create_debt_ratio_donut_chart(bs_data)
        charts.update(debt_chart)
        
        return charts
    
    def create_debt_ratio_donut_chart(self, bs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """부채비율 도넛 차트 생성"""
        if not bs_data:
            return {}
        
        bs_dict = {item['account_nm']: item for item in bs_data}
        
        # 부채와 자본 데이터 추출
        total_debt = safe_convert(bs_dict.get('부채총계', {}).get('thstrm_amount', 0))
        total_equity = safe_convert(bs_dict.get('자본총계', {}).get('thstrm_amount', 0))
        
        if total_debt == 0 and total_equity == 0:
            return {}
        
        # 도넛 차트 생성
        fig = go.Figure(data=[go.Pie(
            labels=['부채', '자본'],
            values=[total_debt, total_equity],
            hole=0.6,
            marker_colors=['#ff7f0e', '#2ca02c'],
            hovertemplate='<b>%{label}</b><br>금액: %{customdata}<br>비율: %{percent:.1%}<extra></extra>',
            customdata=[format_amount(str(int(total_debt))), format_amount(str(int(total_equity)))]
        )])
        
        fig.update_layout(
            title='부채비율 분석',
            height=500,
            **self.chart_config
        )
        
        return {'debt_ratio_donut': fig.to_html(full_html=False, include_plotlyjs=False)}
    
    def create_financial_charts(self, financial_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """재무제표 차트 생성 - 요청된 배치 순서로 생성"""
        if not financial_data:
            print("❌ 재무 데이터가 없습니다.")
            return {}
        
        # 재무상태표와 손익계산서 데이터 분리
        bs_data = [item for item in financial_data if item.get('sj_div') == 'BS']
        is_data = [item for item in financial_data if item.get('sj_div') == 'IS']
        
        print(f"📊 BS 데이터: {len(bs_data)}개, IS 데이터: {len(is_data)}개")
        
        charts = {}
        
        # 1. 재무상태표 차트 (막대그래프 + 텍스트 테이블)
        if bs_data:
            print("📈 재무상태표 차트 생성 중...")
            bs_chart = self.create_balance_sheet_chart(bs_data)
            charts.update(bs_chart)
            print(f"✅ 재무상태표 차트 생성 완료: {len(bs_chart)}개")
        
        # 2. 손익계산서 차트 (막대그래프 + 텍스트 테이블)
        if is_data:
            print("📈 손익계산서 차트 생성 중...")
            is_chart = self.create_income_statement_chart(is_data)
            charts.update(is_chart)
            print(f"✅ 손익계산서 차트 생성 완료: {len(is_chart)}개")
        
        # 3. 주요 재무비율 차트 (수익성 분석 + 부채비율 분석)
        if bs_data and is_data:
            print("📈 주요 재무비율 차트 생성 중...")
            
            # 3-1. 수익성 분석 (방사형차트)
            profitability_chart = self.create_profitability_radar_chart(bs_data, is_data)
            charts.update(profitability_chart)
            
            # 3-2. 부채비율 분석 (도넛차트)
            debt_ratio_chart = self.create_debt_ratio_donut_chart(bs_data)
            charts.update(debt_ratio_chart)
            
            print(f"✅ 주요 재무비율 차트 생성 완료")
        
        # 4. 나머지 요소들 (기존 통합 차트는 하위에 배치)
        if bs_data and is_data:
            print("📈 기타 재무비율 차트 생성 중...")
            combined_charts = self.create_combined_financial_ratios_chart(bs_data, is_data)
            charts.update(combined_charts)
            print(f"✅ 기타 재무비율 차트 생성 완료: {len(combined_charts)}개")
        
        print(f"🎯 총 생성된 차트 수: {len(charts)}개")
        return charts
    
    def create_period_charts(self, financial_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """기간별 차트 생성"""
        if not financial_data:
            return {}
        
        # 데이터프레임 생성
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
        
        charts = {}
        
        # 연도별 재무비율 추이
        ratio_trends = self.create_ratio_trend_chart(year_data)
        if ratio_trends:
            charts.update(ratio_trends)
        
        # 연도별 주요 지표 추이
        indicator_trends = self.create_indicator_trend_chart(year_data)
        if indicator_trends:
            charts.update(indicator_trends)
        
        return charts
    
    def create_ratio_trend_chart(self, year_data: Dict[str, Any]) -> Dict[str, Any]:
        """재무비율 추이 차트 생성"""
        years = sorted(year_data.keys())
        roe_values = []
        roa_values = []
        
        for year in years:
            bs_data = year_data[year]['BS']
            is_data = year_data[year]['IS']
            
            if not bs_data or not is_data:
                continue
            
            bs_dict = {item['account_nm']: item for item in bs_data}
            is_dict = {item['account_nm']: item for item in is_data}
            
            # ROE 계산
            net_income = safe_convert(is_dict.get('당기순이익', {}).get('thstrm_amount', 0))
            total_equity = safe_convert(bs_dict.get('자본총계', {}).get('thstrm_amount', 0))
            roe = (net_income / total_equity) * 100 if total_equity > 0 else 0
            roe_values.append(roe)
            
            # ROA 계산
            total_assets = safe_convert(bs_dict.get('자산총계', {}).get('thstrm_amount', 0))
            roa = (net_income / total_assets) * 100 if total_assets > 0 else 0
            roa_values.append(roa)
        
        if not roe_values:
            return {}
        
        # 추이 차트 생성
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years,
            y=roe_values,
            mode='lines+markers',
            name='ROE (%)',
            line=dict(color='rgb(55, 83, 109)', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=years,
            y=roa_values,
            mode='lines+markers',
            name='ROA (%)',
            line=dict(color='rgb(26, 118, 255)', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='재무비율 추이',
            xaxis_title='연도',
            yaxis_title='비율 (%)',
            height=400,
            **self.chart_config
        )
        
        return {'ratio_trend': fig.to_html(full_html=False, include_plotlyjs=False)}
    
    def create_indicator_trend_chart(self, year_data: Dict[str, Any]) -> Dict[str, Any]:
        """주요 지표 추이 차트 생성"""
        years = sorted(year_data.keys())
        revenue_values = []
        net_income_values = []
        
        for year in years:
            is_data = year_data[year]['IS']
            
            if not is_data:
                continue
            
            is_dict = {item['account_nm']: item for item in is_data}
            
            revenue = safe_convert(is_dict.get('매출액', {}).get('thstrm_amount', 0))
            net_income = safe_convert(is_dict.get('당기순이익', {}).get('thstrm_amount', 0))
            
            revenue_values.append(revenue)
            net_income_values.append(net_income)
        
        if not revenue_values:
            return {}
        
        # 추이 차트 생성
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years,
            y=revenue_values,
            mode='lines+markers',
            name='매출액',
            line=dict(color='rgb(158, 202, 225)', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=years,
            y=net_income_values,
            mode='lines+markers',
            name='당기순이익',
            line=dict(color='rgb(94, 158, 217)', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='주요 지표 추이',
            xaxis_title='연도',
            yaxis_title='금액',
            height=400,
            **self.chart_config
        )
        
        return {'indicator_trend': fig.to_html(full_html=False, include_plotlyjs=False)} 