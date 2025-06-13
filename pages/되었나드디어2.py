import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from scipy.stats import linregress

# 스타일: 전체 영역을 가운데 3/5로 제한 + 입력창/체크박스 개선
st.markdown("""
    <style>
    .main .block-container {
        max-width: 900px;
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
        y_candidates = [col for col in df.columns if col != x_col]

        columns_per_row = 2
        total_slots = len(y_candidates)
        
        # 2열로 행 제한 없이 행 우선으로 나누기
        # 즉, 리스트를 2개씩 나누어 각 열에 넣기
        # 각 열은 y_candidates를 행 우선으로 나눈 것
        col_groups = [y_candidates[i::columns_per_row] for i in range(columns_per_row)]
        
        checkbox_cols = st.columns(columns_per_row)
        
        max_rows = max(len(cg) for cg in col_groups)
        for row_idx in range(max_rows):
            for col_idx in range(columns_per_row):
                if row_idx < len(col_groups[col_idx]):
                    col = col_groups[col_idx][row_idx]
                    if checkbox_cols[col_idx].checkbox(col, key=f"y_{col}"):
                        y_selected.append(col)

    with col2:
        use_dual_y = st.checkbox("▶ y축 2개로 나누기 (좌/우)", value=False)
        chart_type = st.radio("▶ 그래프 형태", ["꺾은선 그래프", "산점도", "막대그래프"], horizontal=True)
        show_regression = False
        if chart_type == "산점도":
            show_regression = st.checkbox("📈 회귀선 및 상관계수 표시")

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
            color = pastel_colors[i % len(pastel_colors)]

            if chart_type == "막대그래프":
                fig.add_trace(go.Bar(
                    x=df[x_col],
                    y=df[col],
                    name=col,
                    marker_color=color,
                    yaxis=yaxis,
                    offsetgroup=str(i),
                    hovertemplate=f"{col}: %{{y}} {extract_unit(col)}<extra></extra>"
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[col],
                    mode=mode,
                    name=col,
                    marker=dict(color=color, size=8, opacity=0.6 if chart_type == "산점도" else 1),
                    line=dict(color=color, width=2),
                    yaxis=yaxis,
                    hovertemplate=f"{col}: %{{y}} {extract_unit(col)}<extra></extra>"
                ))

                if chart_type == "산점도" and show_regression and i == 0:
                    slope, intercept, r_value, p_value, std_err = linregress(df[x_col], df[col])
                    reg_line = slope * df[x_col] + intercept
                    fig.add_trace(go.Scatter(
                        x=df[x_col],
                        y=reg_line,
                        mode="lines",
                        name=f"회귀선 ({col})",
                        line=dict(color="black", dash="dot"),
                        hoverinfo="skip"
                    ))
                    fig.add_annotation(
                        xref="paper", yref="paper",
                        x=0.98, y=0.98,
                        text=f"<b>상관계수 r = {r_value:.2f}</b>",
                        showarrow=False,
                        font=dict(size=14, color="black"),
                        bgcolor="#FFF3D3",
                        bordercolor="#666",
                        borderwidth=1,
                        borderpad=6
                    )

        fig.update_layout(
            title=dict(text=graph_title, x=0.5, y=0.95, font=dict(size=24)),
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
