import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("CSV 파일을 이용한 2차원 산점도 시각화")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    try:
        # CSV 파일 읽기 (인코딩 자동 감지 시도)
        try:
            df = pd.read_csv(uploaded_file)
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded_file, encoding='cp949')  # 한글 파일용 예외 처리

        st.subheader("데이터 미리보기")
        st.write(df.head())

        # 숫자형 컬럼만 선택
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

        if len(numeric_cols) < 2:
            st.warning("산점도를 그리기 위해 최소 두 개의 숫자형 열이 필요합니다.")
        else:
            # X축, Y축 선택
            x_axis = st.selectbox("X축 선택", numeric_cols)
            y_axis = st.selectbox("Y축 선택", numeric_cols, index=1 if len(numeric_cols) > 1 else 0)

            # 산점도 그리기
            st.subheader(f"산점도: {x_axis} vs {y_axis}")
            fig, ax = plt.subplots()
            ax.scatter(df[x_axis], df[y_axis], alpha=0.6)
            ax.set_xlabel(x_axis)
            ax.set_ylabel(y_axis)
            ax.set_title(f"{x_axis} vs {y_axis} 산점도")
            st.pyplot(fig)

    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
else:
    st.info("좌측에서 CSV 파일을 업로드해 주세요.")
