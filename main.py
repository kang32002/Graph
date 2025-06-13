import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.title("CSV 파일 산점도 시각화")

uploaded_file = st.file_uploader("CSV 파일을 업로드하세요 (예: *.csv)")

if uploaded_file is not None:
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[-1].lower()

    if ext != ".csv":
        st.error("CSV 파일만 업로드할 수 있습니다.")
    else:
        try:
            # CSV 읽기
            try:
                df = pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                df = pd.read_csv(uploaded_file, encoding="cp949")

            st.subheader("데이터 미리보기")
            st.write(df.head())

            # 숫자형 열 추출
            numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

            if len(numeric_cols) < 2:
                st.warning("숫자형 열이 2개 이상 필요합니다.")
            else:
                x_axis = st.selectbox("X축 선택", numeric_cols)
                y_axis = st.selectbox("Y축 선택", numeric_cols, index=1)

                fig, ax = plt.subplots()
                ax.scatter(df[x_axis], df[y_axis], alpha=0.6)
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                ax.set_title(f"{x_axis} vs {y_axis} 산점도")
                st.pyplot(fig)
        except Exception as e:
            st.error(f"오류 발생: {e}")
else:
    st.info("CSV 파일을 업로드해 주세요.")
