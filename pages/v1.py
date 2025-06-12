import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 기본 설정
st.set_page_config(page_title="📊 엑셀 그래프 시각화", layout="wide")

# 중앙 정렬용 column 레이아웃
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.markdown("<h1 style='text-align: center;'>📊 엑셀 그래프 만들기</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>엑셀 데이터를 업로드하고, 비교할 열을 선택해서 예쁜 그래프를 그려보세요!</p>", unsafe_allow_html=True)
    st.divider()

# 파일 업로드
uploaded_file = st.file_uploader("📂 엑셀 파일 업로드", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ 파일 업로드 성공!")
    st.dataframe(df.head(), use_container_width=True)

    with col2:
        # 그래프 제목
        graph_title = st.text_input("그래프 제목을 입력하세요", value="그래프 제목")

        # x축 선택
        x_col = st.selectbox("🧭 x축으로 사용할 열을 선택하세요", df.columns)

        # y축 열 선택 (checkbox로 최대 2개)
        st.markdown("📊 y축으로 사용할 열을 최대 2개까지 선택하세요:")
        y_selected = []
        for col in df.columns:
            if col != x_col:
                if st.checkbox(col, key=col):
                    y_selected.append(col)

        # 이중 y축 여부
        use_dual_y = st.checkbox("🔀 y축을 좌우 2개로 나눠서 보기 (단위가 다를 때 체크)", value=False)

        if len(y_selected) == 0:
            st.warning("최소 1개의 y축 열을 선택하세요.")
        elif len(y_selected) > 2:
            st.error("2개까지만 선택할 수 있어요.")
        else:
            fig = go.Figure()

            # 첫 번째 y축 데이터
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_selected[0]],
                mode='lines+markers',
                name=y_selected[0],
                yaxis='y1'
            ))

            # 두 번째 y축 데이터
            if len(y_selected) == 2:
                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[y_selected[1]],
                    mode='lines+markers',
                    name=y_selected[1],
                    yaxis='y2' if use_dual_y else 'y1'
                ))

            # 레이아웃 설정
            layout = {
                'title': {
                    'text': f"<b>{graph_title}</b>",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'family': 'Nanum Gothic, sans-serif'}
                },
                'xaxis': {'title': x_col},
                'yaxis': {'title': y_selected[0]},
                'font': {'family': 'Nanum Gothic, sans-serif', 'size': 14},
                'legend': {'x': 0, 'y': 1.15, 'orientation': "h"},
                'margin': {'t': 100, 'b': 50, 'l': 60, 'r': 60}
            }

            if len(y_selected) == 2 and use_dual_y:
                layout['yaxis2'] = {
                    'title': y_selected[1],
                    'overlaying': 'y',
                    'side': 'right'
                }

            fig.update_layout(layout)

            with col2:
                st.plotly_chart(fig, use_container_width=True)
