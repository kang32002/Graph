import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 제목
st.title("학생 건강검사 결과 산점도 시각화")

# CSV 파일 불러오기
csv_file = "교육부_학생건강검사 결과_20151201.csv"
df = pd.read_csv(csv_file, encoding='utf-8')  # encoding이 다를 경우 cp949로 시도

# 데이터 미리보기
st.subheader("데이터 미리보기")
st.write(df.head())

# 선택할 수 있는 열 목록 필터링 (숫자형 데이터만 선택)
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

# 사용자 입력 - X, Y축 선택
st.subheader("산점도 축 선택")
x_axis = st.selectbox("X축 선택", numeric_cols)
y_axis = st.selectbox("Y축 선택", numeric_cols)

# 산점도 그리기
if x_axis and y_axis:
    st.subheader(f"산점도: {x_axis} vs {y_axis}")
    fig, ax = plt.subplots()
    ax.scatter(df[x_axis], df[y_axis], alpha=0.5)
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.set_title(f"{x_axis} vs {y_axis} 산점도")
    st.pyplot(fig)
