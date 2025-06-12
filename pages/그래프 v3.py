import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="📊 엑셀 그래프 만들기", layout="wide")

# ===== 🎨 파스텔톤 색상 팔레트 =====
colors = ['#A5D8FF', '#C5A3FF', '#FFD6A5', '#FFADAD', '#B9FBC0', '#CAEDFF']

# ===== 🖌 사용자 정의 스타일 =====
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        background-color: #ffffff !important;
        font-family: 'Nanum Gothic', sans-serif;
    }
    h1 {
        color: #4a6fa5;
        font-weight: 700;
        padding-top: 0.5rem;
    }
    .stTextInput>div>div>input {
        background-color: #f0f8ff;
        border-radius: 10px;
        border: 1px solid #cce5ff;
        padding: 0.4em;
    }
    .stButton>button {
        background-color: #a2d5f2;
        color: black;
        font-weight: bold;
        border-radius: 10px;
    }
    .stButton>button:hover {
        background-color: #74c0e3;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ===== 🌟 중앙 레이아웃 =====
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("<h1 style='text-align: center;'>📈 엑셀 그래프 만들기</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>데이터를 올리고 원하는 축을 선택하면, 예쁜 파스텔톤 그래프가 완성돼요!</p>", unsafe_allow_html=True)

# ===== 📂 파일 업로드 =====
uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ 업로드 성공! 아래에서 그래프 설정을 해보세요.")
    st.dataframe(df.head(), use_container_width=True)

    with col2:
        graph_title = st.text_input("그래프 제목", value="그래프 제목")
        x_col = st.selectbox("x축 선택", df.columns)

        # y축 선택 (최대 2개)
        st.markdown("y축으로 사용할 열을 <b>최대 2개</b>까지 체크하세요:", unsafe_allow_html=True)
        y_selected = []
        for idx, col in enumerate(df.columns):
            if col != x_col:
                if st.checkbox(col, key=f"y_{col}"):
                    y_selected.append(col)

        use_dual_y = st.checkbox("y축 2개로 나누기 (좌/우)", value=False)
        graph_type = st.radio("그래프 유형 선택", ["꺾은선 그래프", "막대 그래프"], horizontal=True)

        if 0 < len(y_selected) <= 2:
            fig = go.Figure()

            # y축 1번째
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_selected[0]],
                mode='lines+markers' if graph_type == "꺾은선 그래프" else 'markers',
                name=y_selected[0],
                yaxis='y1',
                marker=dict(color=colors[0], size=8),
                line=dict(color=colors[0], width=3),
                hovertemplate=f"{y_selected[0]}: %{y}<extra></extra>"
            ) if graph_type == "꺾은선 그래프" else
                go.Bar(
                    x=df[x_col],
                    y=df[y_selected[0]],
                    name=y_selected[0],
                    marker_color=colors[0],
                    yaxis='y1',
                    hovertemplate=f"{y_selected[0]}: %{y}<extra></extra>"
                )
            )

            # y축 2번째 (옵션)
            if len(y_selected) == 2:
                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[y_selected[1]],
                    mode='lines+markers' if graph_type == "꺾은선 그래프" else 'markers',
                    name=y_selected[1],
                    yaxis='y2' if use_dual_y else 'y1',
                    marker=dict(color=colors[1], size=8),
                    line=dict(color=colors[1], width=3),
                    hovertemplate=f"{y_selected[1]}: %{y}<extra></extra>"
                ) if graph_type == "꺾은선 그래프" else
                    go.Bar(
                        x=df[x_col],
                        y=df[y_selected[1]],
                        name=y_selected[1],
                        marker_color=colors[1],
                        yaxis='y2' if use_dual_y else 'y1',
                        hovertemplate=f"{y_selected[1]}: %{y}<extra></extra>"
                    )
                )

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
        elif len(y_selected) == 0:
            st.warning("y축으로 사용할 데이터를 선택하세요.")
        else:
            st.error("y축은 최대 2개까지 선택 가능합니다.")
