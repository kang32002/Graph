import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 페이지 기본 설정
st.set_page_config(page_title="📊 엑셀 그래프 시각화", layout="wide")

# 제목
st.markdown("<h1 style='text-align: center;'>📊 엑셀 그래프 만들기</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>엑셀 데이터를 올리고, 비교하고 싶은 열을 선택해서 그래프를 만들어 보세요!</p>", unsafe_allow_html=True)
st.divider()

# 파일 업로드
uploaded_file = st.file_uploader("📂 엑셀 파일 업로드", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ 파일 업로드 성공!")
    st.dataframe(df.head())

    # 그래프 제목
    graph_title = st.text_input("그래프 제목을 입력하세요", value="그래프 제목")

    # x축 선택
    x_col = st.selectbox("🧭 x축으로 사용할 열 선택", df.columns)

    # 비교할 y축 열 선택 (2개 이상 가능)
    y_cols = st.multiselect("📊 y축으로 비교할 열 선택 (2개까지)", df.columns)

    # 이중 y축 사용할지 여부
    use_dual_y = st.checkbox("🔀 y축 2개로 나누기 (스케일 다를 경우 사용)", value=False)

    if len(y_cols) == 0:
        st.warning("y축에 표시할 열을 최소 1개 이상 선택하세요.")
    elif len(y_cols) > 2:
        st.error("최대 2개의 열만 비교할 수 있어요.")
    else:
        fig = go.Figure()

        # 첫 번째 y 데이터
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_cols[0]],
            mode='lines+markers',
            name=y_cols[0],
            yaxis='y1'
        ))

        # 두 번째 y 데이터 (이중 y축 사용 시)
        if len(y_cols) == 2:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_cols[1]],
                mode='lines+markers',
                name=y_cols[1],
                yaxis='y2' if use_dual_y else 'y1'
            ))

        # 그래프 레이아웃
        layout = {
            'title': graph_title,
            'xaxis': {'title': x_col},
            'yaxis': {'title': y_cols[0]},
            'font': {'family': 'Nanum Gothic, sans-serif', 'size': 14},
            'legend': {'x': 0, 'y': 1.15, 'orientation': "h"},
            'margin': {'t': 60}
        }

        if len(y_cols) == 2 and use_dual_y:
            layout['yaxis2'] = {
                'title': y_cols[1],
                'overlaying': 'y',
                'side': 'right'
            }

        fig.update_layout(layout)

        st.plotly_chart(fig, use_container_width=True)
