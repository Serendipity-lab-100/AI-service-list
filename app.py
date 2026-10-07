# ============================================
# AI 서비스 리스트 - 추천 + 작업 순서 안내 + 서비스 상세 카드
# 실행 방법: 터미널에 streamlit run app.py
# 필요한 파일: ai_services.csv, workflows.csv (app.py와 같은 폴더)
# ============================================

import streamlit as st   # 웹 화면을 만들어주는 도구
import pandas as pd      # 엑셀처럼 표 데이터를 다루는 도구
from urllib.parse import urlparse  # 주소에서 사이트 이름만 뽑는 도구

# --- 1. 페이지 기본 설정 ---
st.set_page_config(page_title="AI 서비스 리스트", page_icon="🧭", layout="wide")


# --- 2. 데이터 불러오기 (한 번만 읽고 기억) ---
@st.cache_data
def load_data():
    services = pd.read_csv("ai_services.csv", encoding="utf-8-sig").fillna("")
    flows = pd.read_csv("workflows.csv", encoding="utf-8-sig").fillna("")
    return services, flows


df, flows = load_data()

# 서비스 이름으로 주소를 찾는 사전 (예: "Gamma" → "https://gamma.app")
주소사전 = dict(zip(df["서비스명"], df["URL"]))
난이도표시 = {"쉬움": "🟢 쉬움", "보통": "🟡 보통", "어려움": "🔴 어려움"}


def 로고주소(사이트주소):
    """사이트 주소로 그 사이트의 아이콘(로고) 이미지 주소를 만듦"""
    if not 사이트주소:
        return ""
    도메인 = urlparse(사이트주소).netloc
    return f"https://www.google.com/s2/favicons?domain={도메인}&sz=64"


def 서비스카드(행):
    """서비스 한 개를 카드 모양으로 그림: 로고·이름 / 설명 / 주로 쓰는 작업 / 사용 방법 / 버튼"""
    with st.container(border=True):
        로고 = 로고주소(행["URL"])
        로고태그 = f'<img src="{로고}" width="28" style="vertical-align:middle;border-radius:6px;margin-right:8px">' if 로고 else ""
        st.markdown(
            f'{로고태그}<b style="font-size:1.1rem">{행["서비스명"]}</b>&nbsp;&nbsp;{난이도표시.get(행["난이도"], "")}',
            unsafe_allow_html=True,
        )
        st.caption(행["한줄설명"])
        if 행["주로쓰는작업1"]:
            st.markdown(f"**이런 작업에 많이 써요**\n- {행['주로쓰는작업1']}\n- {행['주로쓰는작업2']}")
        if 행["사용방법"]:
            with st.expander("사용 방법 보기"):
                st.write(행["사용방법"])
        if 행["URL"]:
            st.link_button("사이트 열기", 행["URL"], use_container_width=True)
        else:
            st.caption("주소 확인 중")


# --- 3. 추천 계산 함수 ---
def 글자정리(글):
    """띄어쓰기를 없애고 소문자로 바꿔서 비교하기 쉽게 만듦"""
    return 글.replace(" ", "").lower()


def 작업찾기(입력):
    """입력한 문장과 키워드가 가장 많이 겹치는 작업(시나리오)을 찾음"""
    입력 = 글자정리(입력)
    최고점수, 최고작업 = 0, None
    for 작업명, 묶음 in flows.groupby("작업명", sort=False):
        키워드들 = 묶음["키워드"].iloc[0].split(",")
        점수 = sum(1 for k in 키워드들 if 글자정리(k) in 입력)
        if 점수 > 최고점수:
            최고점수, 최고작업 = 점수, 작업명
    return 최고작업


def 서비스찾기(입력):
    """맞는 작업이 없을 때: 서비스별 키워드로 점수를 매겨 상위 3개를 고름"""
    입력 = 글자정리(입력)
    점수표 = df.copy()
    점수표["점수"] = 점수표["키워드"].apply(
        lambda 키: sum(1 for k in 키.split(",") if k and 글자정리(k) in 입력)
    )
    점수표 = 점수표[(점수표["점수"] > 0) & (점수표["난이도"] != "어려움")]
    점수표 = 점수표.drop_duplicates("서비스명")
    return 점수표.sort_values("점수", ascending=False).head(3)


# --- 4. 화면 맨 위: 제목과 입력창 ---
st.title("🧭 AI 서비스 리스트")
st.caption("하고 싶은 작업을 적으면, 쓸 만한 AI 3개와 진행 순서를 알려드려요.")

# 예시 버튼을 누르면 입력창에 글자가 들어가게 하는 함수
def 예시넣기(문장):
    st.session_state["입력창"] = 문장

입력 = st.text_input(
    "무슨 작업을 하려고 하나요?",
    key="입력창",
    placeholder="예: 다음 주 조별 발표 PPT를 만들어야 해요",
)

st.write("이런 걸 입력해 보세요")
예시들 = ["발표자료 만들기", "회의록 정리", "유튜브 영상 요약해서 공부", "카드뉴스 만들기", "자소서 쓰기"]
버튼칸 = st.columns(len(예시들))
for 칸, 문장 in zip(버튼칸, 예시들):
    칸.button(문장, on_click=예시넣기, args=(문장,), use_container_width=True)


# --- 5. 추천 결과 보여주기 ---
if 입력:
    작업 = 작업찾기(입력)

    if 작업:
        st.success(f"**{작업}** 작업으로 이해했어요. 이 순서로 진행해 보세요.")
        단계들 = flows[flows["작업명"] == 작업].sort_values("순서")
        칸들 = st.columns(len(단계들))
        for 칸, (_, 단계) in zip(칸들, 단계들.iterrows()):
            with 칸:
                with st.container(border=True):
                    로고 = 로고주소(주소사전.get(단계["서비스명"], ""))
                    st.markdown(
                        f'<img src="{로고}" width="24" style="vertical-align:middle;border-radius:6px;margin-right:6px">'
                        f'<b>{단계["순서"]}단계 · {단계["서비스명"]}</b>',
                        unsafe_allow_html=True,
                    )
                    st.write(단계["할일"])
                    st.caption("이렇게 입력해 보세요 (오른쪽 위 아이콘으로 복사)")
                    st.code(단계["예시입력"], language=None, wrap_lines=True)
                    주소 = 주소사전.get(단계["서비스명"], "")
                    if 주소:
                        st.link_button("사이트 열기", 주소, use_container_width=True)
        st.info("💡 AI 결과는 초안이에요. 사실 여부와 출처는 꼭 직접 확인하세요.")

    else:
        후보 = 서비스찾기(입력)
        if len(후보) > 0:
            st.warning("딱 맞는 작업 순서는 아직 없지만, 관련 있어 보이는 서비스예요.")
            칸들 = st.columns(3)
            for 칸, (_, 행) in zip(칸들, 후보.iterrows()):
                with 칸:
                    서비스카드(행)
        else:
            st.error("관련 서비스를 찾지 못했어요. 위 예시처럼 '무엇을 만들고 싶은지' 적어보세요.")

st.divider()


# --- 6. 아래쪽: 전체 서비스 목록 (3단계와 동일) ---
st.header("전체 AI 서비스 둘러보기")
분야목록 = ["전체"] + list(df["분야"].unique())
선택분야 = st.sidebar.radio("분야 선택", 분야목록)
보여줄데이터 = df if 선택분야 == "전체" else df[df["분야"] == 선택분야]

for 분야 in 보여줄데이터["분야"].unique():
    st.subheader(분야)
    이분야 = 보여줄데이터[보여줄데이터["분야"] == 분야]
    칸 = st.columns(3)
    for 순번, (_, 행) in enumerate(이분야.iterrows()):
        with 칸[순번 % 3]:
            서비스카드(행)


# --- 7. 출처 표기 ---
st.divider()
st.caption("서비스 분류 원본: Threads @choi.openai 「분야별 무조건 알아야하는 AI 서비스 리스트」")
