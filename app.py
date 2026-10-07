# ============================================
# AI 서비스 리스트 - 3단계: 기본 목록 화면
# 실행 방법: 터미널에 streamlit run app.py
# ============================================

import streamlit as st   # 웹 화면을 만들어주는 도구
import pandas as pd      # 엑셀처럼 표 데이터를 다루는 도구

# --- 1. 페이지 기본 설정 (브라우저 탭 제목, 화면 너비) ---
st.set_page_config(page_title="AI 서비스 리스트", page_icon="🧭", layout="wide")


# --- 2. 데이터 불러오기 ---
# @st.cache_data : 파일을 한 번만 읽고 기억해 두라는 뜻 (화면이 빨라짐)
@st.cache_data
def load_data():
    df = pd.read_csv("ai_services.csv", encoding="utf-8-sig")
    df = df.fillna("")  # 빈 칸을 오류 없이 빈 글자로 바꿈
    return df


df = load_data()


# --- 3. 화면 맨 위 제목 ---
st.title("🧭 AI 서비스 리스트")
st.caption("하고 싶은 작업에 맞는 AI를 찾아보세요. 카드를 누르면 해당 사이트로 이동합니다.")


# --- 4. 왼쪽 사이드바: 분야 선택 ---
분야목록 = ["전체"] + list(df["분야"].unique())
선택분야 = st.sidebar.radio("분야 선택", 분야목록)

if 선택분야 != "전체":
    보여줄데이터 = df[df["분야"] == 선택분야]
else:
    보여줄데이터 = df


# --- 5. 서비스 카드 그리기 ---
난이도표시 = {"쉬움": "🟢 쉬움", "보통": "🟡 보통", "어려움": "🔴 어려움"}

for 분야 in 보여줄데이터["분야"].unique():
    st.subheader(분야)
    이분야 = 보여줄데이터[보여줄데이터["분야"] == 분야]

    칸 = st.columns(3)  # 한 줄에 카드 3개씩
    for 순번, (_, 행) in enumerate(이분야.iterrows()):
        with 칸[순번 % 3]:
            with st.container(border=True):
                st.markdown(f"**{행['서비스명']}**  ·  {난이도표시.get(행['난이도'], '')}")
                st.write(행["한줄설명"])
                if 행["URL"]:
                    st.link_button("사이트 열기", 행["URL"], use_container_width=True)
                else:
                    st.caption("주소 확인 중")


# --- 6. 맨 아래 출처 표기 ---
st.divider()
st.caption("서비스 분류 원본: Threads @choi.openai 「분야별 무조건 알아야하는 AI 서비스 리스트」")
