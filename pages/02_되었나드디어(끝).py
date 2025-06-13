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

        columns_per_row = 2  # 2열로 변경
        rows = (len(y_candidates) + columns_per_row - 1) // columns_per_row
        padded_cols = y_candidates + [""] * (rows * columns_per_row - len(y_candidates))
        grid = [padded_cols[i*columns_per_row:(i+1)*columns_per_row] for i in range(rows)]

        checkbox_cols = st.columns(columns_per_row)

        for row in grid:
            for col_idx, col in enumerate(row):
                if col:
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
                    # 결측치 있는 행 제거 후 회귀선 및 상관계수 계산
                    valid_data = df[[x_col, col]].dropna()
                    if len(valid_data) > 1:
                        slope, intercept, r_value, p_value, std_err = linregress(valid_data[x_col], valid_data[col])
                        reg_line = slope * valid_data[x_col] + intercept
                        fig.add_trace(go.Scatter(
                            x=valid_data[x_col],
                            y=reg_line,
                            mode="lines",
                            name=f"회귀선 ({col})",
                            line=dict(color="#003366", dash="dot"),  # 진한 파란색으로 변경
                            hoverinfo="skip"
                        ))
                        fig.add_annotation(
                            xref="paper", yref="paper",
                            x=0.98, y=0.98,
                            text=f"<b>상관계수 r = {r_value:.2f}</b>",
                            showarrow=False,
                            font=dict(size=14, color="black"),
                            bgcolor="rgba(255, 243, 211, 0.3)",  # 배경 투명도 30%
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
import os

st.subheader("4️⃣ 📬 분석 의견을 남겨주세요")
opinion_file = "opinions.csv"

col1, col2 = st.columns([1, 3])
with col1:
    user_name = st.text_input("이름", max_chars=20)
with col2:
    user_opinion = st.text_area("분석 의견 (예: 상관관계 해석, 데이터 특이사항 등)", height=100)

submit_button = st.button("✏️ 의견 등록")

if submit_button and user_name.strip() and user_opinion.strip():
    from datetime import datetime
    new_entry = pd.DataFrame([{
        "작성시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "이름": user_name.strip(),
        "의견": user_opinion.strip()
    }])

    if os.path.exists(opinion_file):
        old_data = pd.read_csv(opinion_file)
        all_data = pd.concat([old_data, new_entry], ignore_index=True)
    else:
        all_data = new_entry

    all_data.to_csv(opinion_file, index=False)
    st.success("의견이 성공적으로 등록되었습니다!")
elif submit_button:
    st.warning("이름과 의견을 모두 입력해주세요.")

# 저장된 의견 보여주기 및 삭제 기능
if os.path.exists(opinion_file):
    st.markdown("### 💬 등록된 의견 (최신순)")
    opinion_data = pd.read_csv(opinion_file)
    opinion_data = opinion_data[::-1].reset_index(drop=True)

    for i, row in opinion_data.iterrows():
        with st.container():
            st.markdown(f"**🧑‍💼 {row['이름']}** ({row['작성시간']})")
            st.markdown(f"> {row['의견']}")
            delete_key = f"delete_{i}"
            if st.button("🗑️ 삭제", key=delete_key):
                opinion_data.drop(i, inplace=True)
                opinion_data[::-1].to_csv(opinion_file, index=False)  # 저장은 다시 최신순으로
                st.success("의견이 삭제되었습니다.")
                st.experimental_rerun()
else:
    st.info("아직 등록된 의견이 없습니다.")
