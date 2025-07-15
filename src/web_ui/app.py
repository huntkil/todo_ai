import streamlit as st
import requests
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any

# 페이지 설정
st.set_page_config(
    page_title="Work Automation AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API 엔드포인트
API_BASE_URL = "http://localhost:8000"

def main():
    st.title("🤖 Work Automation AI")
    st.markdown("---")
    
    # 사이드바
    with st.sidebar:
        st.header("📋 메뉴")
        page = st.selectbox(
            "페이지 선택",
            ["🏠 대시보드", "📝 업무 입력", "📅 캘린더", "📊 Gantt 차트", "📓 Obsidian 노트"]
        )
    
    # 페이지 라우팅
    if page == "🏠 대시보드":
        show_dashboard()
    elif page == "📝 업무 입력":
        show_work_input()
    elif page == "📅 캘린더":
        show_calendar()
    elif page == "📊 Gantt 차트":
        show_gantt_chart()
    elif page == "📓 Obsidian 노트":
        show_obsidian_notes()

def show_dashboard():
    """대시보드 페이지"""
    st.header("🏠 대시보드")
    
    # 통계 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 작업", "12", "+2")
    
    with col2:
        st.metric("진행 중", "5", "-1")
    
    with col3:
        st.metric("완료", "7", "+3")
    
    with col4:
        st.metric("일정", "8", "+1")
    
    # 차트 영역
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 작업 진행률")
        progress_data = {
            '상태': ['완료', '진행 중', '대기'],
            '개수': [7, 5, 3]
        }
        df = pd.DataFrame(progress_data)
        fig = px.pie(df, values='개수', names='상태', title='작업 상태 분포')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 일별 작업 완료")
        daily_data = {
            '날짜': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
            '완료': [2, 3, 1, 4, 2]
        }
        df = pd.DataFrame(daily_data)
        fig = px.bar(df, x='날짜', y='완료', title='일별 완료 작업 수')
        st.plotly_chart(fig, use_container_width=True)

def show_work_input():
    """업무 입력 페이지"""
    st.header("📝 업무 입력")
    
    # 입력 폼
    with st.form("work_input_form"):
        st.subheader("업무 내용 입력")
        
        work_text = st.text_area(
            "업무 내용을 입력하세요",
            placeholder="예: 내일 오후 3시에 클라이언트와 회의가 있습니다. 프로젝트 진행 상황을 보고드릴 예정입니다.",
            height=150
        )
        
        user_id = st.text_input("사용자 ID", value="user1")
        
        submitted = st.form_submit_button("분석 및 처리")
        
        if submitted and work_text:
            with st.spinner("AI가 업무를 분석하고 있습니다..."):
                try:
                    # API 호출
                    response = requests.post(
                        f"{API_BASE_URL}/process_work_input",
                        json={
                            "text": work_text,
                            "user_id": user_id,
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        show_processing_result(result)
                    else:
                        st.error(f"API 호출 실패: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"오류 발생: {str(e)}")

def show_processing_result(result: Dict[str, Any]):
    """처리 결과 표시"""
    st.success("✅ 업무 분석 완료!")
    
    # 결과 요약
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 분석 결과")
        st.write(f"**분류**: {result['category']}")
        st.write(f"**키워드**: {', '.join(result['structured_data'].get('keywords', []))}")
        st.write(f"**감정**: {result['structured_data'].get('sentiment', 'neutral')}")
    
    with col2:
        st.subheader("📊 생성된 항목")
        st.write(f"📅 캘린더 이벤트: {len(result['calendar_events'])}개")
        st.write(f"📓 Obsidian 노트: {len(result['obsidian_notes'])}개")
        st.write(f"📊 Gantt 작업: {len(result['gantt_tasks'])}개")
    
    # 상세 결과
    with st.expander("📋 상세 분석 결과"):
        st.json(result['structured_data'])
    
    # 생성된 항목들 표시
    if result['calendar_events']:
        with st.expander("📅 생성된 캘린더 이벤트"):
            for event in result['calendar_events']:
                st.write(f"**{event.get('summary', '제목 없음')}**")
                st.write(f"시간: {event.get('start_time', 'N/A')} ~ {event.get('end_time', 'N/A')}")
                st.write(f"설명: {event.get('description', '설명 없음')}")
                st.divider()
    
    if result['obsidian_notes']:
        with st.expander("📓 생성된 Obsidian 노트"):
            for note in result['obsidian_notes']:
                st.write(f"**{note.get('filename', '파일명 없음')}**")
                st.write(f"경로: {note.get('path', 'N/A')}")
                st.write(f"생성: {note.get('created_at', 'N/A')}")
                st.divider()
    
    if result['gantt_tasks']:
        with st.expander("📊 생성된 Gantt 작업"):
            for task in result['gantt_tasks']:
                st.write(f"**{task.get('title', '제목 없음')}**")
                st.write(f"상태: {task.get('status', 'N/A')}")
                st.write(f"진행률: {task.get('progress', 0)}%")
                st.write(f"담당자: {task.get('assignee', 'N/A')}")
                st.divider()

def show_calendar():
    """캘린더 페이지"""
    st.header("📅 캘린더")
    
    # 캘린더 뷰 (간단한 표 형태)
    st.subheader("이번 주 일정")
    
    # 샘플 데이터
    calendar_data = {
        '시간': ['09:00', '14:00', '16:00', '10:00', '15:00'],
        '일정': ['팀 미팅', '클라이언트 미팅', '코드 리뷰', '프로젝트 계획', '문서 작성'],
        '상태': ['완료', '예정', '예정', '진행 중', '대기']
    }
    
    df = pd.DataFrame(calendar_data)
    st.dataframe(df, use_container_width=True)
    
    # 일정 추가
    with st.expander("➕ 새 일정 추가"):
        with st.form("add_event_form"):
            event_title = st.text_input("일정 제목")
            event_date = st.date_input("날짜")
            event_time = st.time_input("시간")
            event_desc = st.text_area("설명")
            
            if st.form_submit_button("일정 추가"):
                st.success("일정이 추가되었습니다!")

def show_gantt_chart():
    """Gantt 차트 페이지"""
    st.header("📊 Gantt 차트")
    
    # 샘플 Gantt 데이터
    gantt_data = {
        'Task': ['프로젝트 기획', '디자인', '개발', '테스트', '배포'],
        'Start': ['2024-01-01', '2024-01-05', '2024-01-10', '2024-01-20', '2024-01-25'],
        'Finish': ['2024-01-04', '2024-01-09', '2024-01-19', '2024-01-24', '2024-01-30'],
        'Progress': [100, 80, 60, 20, 0]
    }
    
    df = pd.DataFrame(gantt_data)
    
    # Gantt 차트 생성
    fig = go.Figure()
    
    for i, task in df.iterrows():
        fig.add_trace(go.Bar(
            name=task['Task'],
            x=[task['Finish']],
            y=[task['Task']],
            orientation='h',
            marker=dict(
                color=f'rgba(100, 149, 237, {task["Progress"]/100})',
                line=dict(color='rgba(58, 71, 80, 0.6)', width=1)
            ),
            text=f"{task['Progress']}%",
            textposition='auto',
        ))
    
    fig.update_layout(
        title="프로젝트 일정",
        xaxis_title="날짜",
        yaxis_title="작업",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 작업 목록
    st.subheader("📋 작업 목록")
    st.dataframe(df, use_container_width=True)

def show_obsidian_notes():
    """Obsidian 노트 페이지"""
    st.header("📓 Obsidian 노트")
    
    # 노트 목록
    st.subheader("📁 최근 노트")
    
    # 샘플 노트 데이터
    notes_data = {
        '제목': ['업무일지 2024-01-15', '회의록 - 프로젝트 킥오프', '일정 - 클라이언트 미팅'],
        '카테고리': ['업무일지', '회의록', '일정'],
        '생성일': ['2024-01-15', '2024-01-14', '2024-01-13'],
        '태그': ['#업무일지 #work', '#회의록 #meeting', '#일정 #schedule']
    }
    
    df = pd.DataFrame(notes_data)
    st.dataframe(df, use_container_width=True)
    
    # 노트 내용 미리보기
    with st.expander("📄 노트 내용 미리보기"):
        st.markdown("""
        # 업무일지 - 2024-01-15
        
        ## 주요 작업
        오늘은 프로젝트 기획 단계를 완료했습니다.
        
        ## 완료 사항
        1. 요구사항 분석 완료
        2. 시스템 아키텍처 설계
        3. 개발 일정 수립
        
        ## 키워드
        프로젝트, 기획, 설계, 일정
        
        ## 관련 인물
        김개발, 이기획
        
        ## 메모
        - 처리 시간: 2024-01-15T18:30:00
        - 감정: positive
        
        ---
        태그: #업무일지 #work #2024/01/15
        """)

if __name__ == "__main__":
    main() 