import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import re

# 스타일: 파스텔톤 입력창 및 체크박스
st.markdown("""
    <style>
    input[type="text"] {
        background-color: #f0f4ff !important;
        color: #333333 !important;
        border-radius: 10px;
        border: 1px solid #a2d5f2;
        padding: 0.5rem;
    }
    .stCheckbox > div {
        background-color: #f9f9ff;
        border-radius: 8px;
        padding: 5px;
    }
    .checkbox-scroll {
        height: 150px;
        overflow-y: scroll;
        border: 1px solid #ccc;
        padding: 10px;
        border-radius: 10px;
        background-color: #f0f4ff;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌈 데이터 그래프 만들기")

uploaded_file = st.file_uploader("📁 엑셀 파일을 업로드하세요", type=["xlsx"])

def extract_unit(col_name):
    match = re.search(r"\\((.*?)\\)", col_name)
    return match.group(1) if match else ""

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("1️⃣ 그래프 제목 입력")
    graph_title = st.text_input("여기에 제목을 입력하세요", value="나의 멋진 그래프")

    st.subheader("2️⃣ x축 데이터 선택")
    x_col = st.selectbox("x축에 사용할 열을 선택하세요", df.columns, key="xcol")

    st.subheader("3️⃣ y축 데이터 및 옵션")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("✔️ y축에 사용할 열 (최대 2개)")
        y_selected = []
        with st.container():
            st.markdown('<div class="checkbox-scroll">', unsafe_allow_html=True)
            for col in df.columns:
                if col != x_col:
                    if st.checkbox(col, key=f"y_{col}"):
                        y_selected.append(col)
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        use_dual_y = st.checkbox("▶ y축 2개로 나누기 (좌/우)", value=False)
        chart_type = st.radio("▶ 그래프 형태", ["꺾은선 그래프", "산점도", "막대그래프"], horizontal=True)

    # 파스텔톤 색상
    pastel_colors = [
        "#A0D8B3", "#AED9E0", "#FFB5E8", "#FFDAC1", "#CBAACB", "#F6DFEB",
        "#C7CEEA", "#E0BBE4", "#B5EAD7", "#FFABAB"
    ]

    if y_selected:
        fig = go.Figure()
        for i, col in enumerate(y_selected):
            yaxis = "y2" if use_dual_y and i == 1 else "y"
            unit = extract_unit(col)

            if chart_type == "막대그래프":
                fig.add_trace(go.Bar(
                    x=df[x_col],
                    y=df[col],
                    name=col,
                    marker=dict(color=pastel_colors[i % len(pastel_colors)]),
                    yaxis=yaxis,
                    hovertemplate=f"{col}: %{{y}} {unit}<extra></extra>"
                ))
            else:
                mode = "lines+markers" if chart_type == "꺾은선 그래프" else "markers"
                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[col],
                    mode=mode,
                    name=col,
                    marker=dict(color=pastel_colors[i % len(pastel_colors)], size=8),
                    line=dict(color=pastel_colors[i % len(pastel_colors)], width=2),
                    yaxis=yaxis,
                    hovertemplate=f"{col}: %{{y}} {unit}<extra></extra>",
                ))

        layout = dict(
            title=dict(text=graph_title, x=0.5, y=0.95, font=dict(size=24)),
            xaxis_title=x_col,
            yaxis_title=y_selected[0],
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            height=500,
            width=900,
            margin=dict(t=80, b=100),
        )

        if use_dual_y and len(y_selected) > 1:
            layout["yaxis2"] = dict(
                title=y_selected[1],
                overlaying="y",
                side="right",
                showgrid=False
            )

        fig.update_layout(**layout)

        st.plotly_chart(fig, use_container_width=True)

        # PNG 저장 기능
        import kaleido  # pip install kaleido 필요
        img_bytes = fig.to_image(format="png", engine="kaleido", width=1000, height=600)
        st.download_button(
            label="📥 그래프 PNG로 저장하기",
            data=img_bytes,
            file_name=f"{graph_title}.png",
            mime="image/png"
        )
    else:
        st.info("y축으로 사용할 데이터를 하나 이상 선택해주세요.")
