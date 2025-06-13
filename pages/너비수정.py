import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import io
from PIL import Image
import numpy as np  # 회귀선 계산용

# 전체 영역 스타일: 가로 60%, 가운데 정렬
st.markdown("""
    <style>
    .main .block-container {
        width: 60%;
        max-width: 60%;
        margin: auto;
    }
    input[type="text"] {
        background-color: #f0f4ff !important;
        color: #333333 !important;
        border-radius: 10px;
        border: 1px solid #a2d5f2;
        padding: 0.5rem;
    }
    .checkbox-container {
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌈 데이터 그래프 만들기")

uploaded_file = st.file_uploader("📁 엑셀 파일을 업로드하세요", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("1️⃣ 그래프 제목 입력")
    graph_title = st.text_input("여기에 제목을 입력하세요", value="나의 멋진 그래프")

    st.subheader("2️⃣ x축 데이터 선택")
    x_col = st.selectbox("x축에 사용할 열을 선택하세요", df.columns, key="xcol")

    st.subheader("3️⃣ y축 데이터 및 옵션")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("✔️ y축에 사용할 열을 선택 (최대 2개)")
        y_selected = []
        for col in df.columns:
            if col != x_col:
                if st.checkbox(col, key=f"y_{col}"):
                    y_selected.append(col)

    with col2:
        use_dual_y = st.checkbox("▶ y축 2개로 나누기 (좌/우)", value=False)
        chart_type = st.radio("▶ 그래프 형태", ["꺾은선 그래프", "산점도", "막대그래프"], horizontal=True)

        # 산점도 옵션
        show_regression = show_corr = False
        if chart_type == "산점도" and len(y_selected) == 1:
            show_regression = st.checkbox("📈 회귀선 추가", value=False)
            show_corr = st.checkbox("📊 상관계수 표시", value=False)

    pastel_colors = [
        "#A0D8B3", "#AED9E0", "#FFB5E8", "#FFDAC1", "#CBAACB", "#F6DFEB",
        "#C7CEEA", "#E0BBE4", "#B5EAD7", "#FFABAB"
    ]

    def extract_unit(col_name):
        import re
        match = re.search(r"\((.*?)\)", col_name)
        return match.group(1) if match else ""

    if y_selected:
        fig = go.Figure()

        for i, col in enumerate(y_selected):
            yaxis = "y2" if use_dual_y and i == 1 else "y"
            mode = "lines+markers" if chart_type == "꺾은선 그래프" else "markers"

            if chart_type == "막대그래프":
                fig.add_trace(go.Bar(
                    x=df[x_col],
                    y=df[col],
                    name=col,
                    marker_color=pastel_colors[i % len(pastel_colors)],
                    yaxis=yaxis,
                    offsetgroup=str(i),
                    hovertemplate=f"{col}: %{{y}} {extract_unit(col)}<extra></extra>"
                ))
            elif chart_type == "산점도":
                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[col],
                    mode=mode,
                    name=col,
                    marker=dict(color=pastel_colors[i % len(pastel_colors)], size=8, opacity=0.6),
                    yaxis=yaxis,
                    hovertemplate=f"{col}: %{{y}} {extract_unit(col)}<extra></extra>"
                ))

                # 회귀선
                if show_regression and len(y_selected) == 1:
                    x_vals = df[x_col].dropna()
                    y_vals = df[col].dropna()
                    if x_vals.shape[0] == y_vals.shape[0] and x_vals.shape[0] > 1:
                        coeffs = np.polyfit(x_vals, y_vals, deg=1)
                        reg_line = coeffs[0] * x_vals + coeffs[1]
                        fig.add_trace(go.Scatter(
                            x=x_vals,
                            y=reg_line,
                            mode="lines",
                            name="회귀선",
                            line=dict(color="#0044cc", dash="dash")  # 진한 파랑
                        ))

                # 상관계수 텍스트 카드
                if show_corr and len(y_selected) == 1:
                    corr_val = df[[x_col, col]].corr().iloc[0, 1]
                    fig.add_annotation(
                        text=f"<b>상관계수<br>r = {corr_val:.2f}</b>",
                        xref="paper", yref="paper",
                        x=0.95, y=0.95, showarrow=False,
                        font=dict(size=16, color="#222222"),
                        align="center",
                        bgcolor="rgba(255, 255, 255, 0.5)",
                        bordercolor="#cccccc",
                        borderwidth=2,
                        borderpad=10
                    )
            else:
                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[col],
                    mode=mode,
                    name=col,
                    marker=dict(color=pastel_colors[i % len(pastel_colors)], size=8),
                    line=dict(color=pastel_colors[i % len(pastel_colors)], width=2),
                    yaxis=yaxis,
                    hovertemplate=f"{col}: %{{y}} {extract_unit(col)}<extra></extra>"
                ))

        fig.update_layout(
            title=dict(text=graph_title, x=0.5, y=0.95, font=dict(size=24)),  # 제목 가운데
            xaxis_title=x_col,
            yaxis_title=y_selected[0],
            yaxis2=dict(
                title=y_selected[1] if use_dual_y and len(y_selected) > 1 else "",
                overlaying="y",
                side="right",
                showgrid=False
            ) if use_dual_y and len(y_selected) > 1 else None,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            height=500,
            width=900,
            margin=dict(t=80, b=100)
        )

        st.plotly_chart(fig, use_container_width=True)

        import kaleido  # pip install kaleido 필요
        img_bytes = fig.to_image(format="png", engine="kaleido", width=1000, height=600)
        st.download_button(
            label="📅 그래프 PNG로 저장하기",
            data=img_bytes,
            file_name=f"{graph_title}.png",
            mime="image/png"
        )
    else:
        st.info("y축으로 사용할 데이터를 하나 이상 선택해주세요.")
