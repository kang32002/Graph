import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 페이지 설정 (기본 밝은 테마 유지)
st.set_page_config(page_title="📊 엑셀 그래프 만들기", layout="wide")

# ====== 🎨 사용자 정의 스타일 추가 ======
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
    .stSelectbox, .stCheckbox {
        background-color: #f8faff !important;
        border-radius: 12px;
    }
    .stButton>button {
        background-color: #a2d5f2;
        color: black;
        font-weight: bold;
        border-radius: 10px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #74c0e3;
        color: white;
    }
    .stDataFrame {
        border: 1px solid #eee;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# ====== 🧭 중앙 레이아웃 설정 ======
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.markdown("<h1 style='text-align: center;'>🎨 나만의 엑셀 그래프 만들기</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px;'>엑셀 데이터를 올리고, x축과 y축을 선택해서 예쁜 그래프를 만들어보세요!</p>", unsafe_allow_html=True)
    st.divider()

uploaded_file = st.file_uploader("📂 엑셀 파일 업로드", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ 파일 업로드 성공!")
    st.dataframe(df.head(), use_container_width=True)

    with col2:
        graph_title = st.text_input("📌 그래프 제목을 입력하세요", value="그래프 제목")

        x_col = st.selectbox("🔹 x축으로 사용할 열 선택", df.columns)

        st.markdown("🔸 y축으로 사용할 열을 <b>최대 2개</b>까지 체크하세요:", unsafe_allow_html=True)
        y_selected = []
        for col in df.columns:
            if col != x_col:
                if st.checkbox(col, key=col):
                    y_selected.append(col)

        use_dual_y = st.checkbox("🔀 y축을 좌/우 2개로 나누기 (단위 다를 때 체크)", value=False)

        if len(y_selected) == 0:
            st.warning("y축으로 최소 1개 이상 선택하세요.")
        elif len(y_selected) > 2:
            st.error("y축은 최대 2개까지만 선택할 수 있어요.")
        else:
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_selected[0]],
                mode='lines+markers',
                name=y_selected[0],
                yaxis='y1'
            ))

            if len(y_selected) == 2:
                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[y_selected[1]],
                    mode='lines+markers',
                    name=y_selected[1],
                    yaxis='y2' if use_dual_y else 'y1'
                ))

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
