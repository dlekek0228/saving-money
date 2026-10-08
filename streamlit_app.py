import os
import pandas as pd
import streamlit as st

# CSV 파일명 설정
DATA_FILE = "pocket_money.csv"


# --- 1. 데이터 불러오기 및 저장 함수 ---
def load_data():
    """CSV 파일에서 데이터를 안전하게 불러옵니다."""
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE, encoding="utf-8-sig")
        except Exception:
            # 파일 읽기 실패 시 새로 생성
            return pd.DataFrame(columns=["구분", "분류", "내용", "금액(원)"])
    else:
        return pd.DataFrame(columns=["구분", "분류", "내용", "금액(원)"])


def save_data(df):
    """데이터프레임을 CSV 파일로 저장합니다."""
    df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")


# --- 2. 앱 기본 설정 및 세션 로드 ---
st.set_page_config(
    page_title="용돈기입장", page_icon="💰", layout="centered"
)
st.title("💰 나만의 용돈기입장")

if "records_df" not in st.session_state:
    st.session_state.records_df = load_data()

# --- 3. 사이드바: 내역 추가 ---
st.sidebar.header("✏️ 내역 추가하기")

type_option = st.sidebar.radio(
    "구분", ["수입 (+)", "지출 (-)"], key="type_option_radio"
)

category = st.sidebar.text_input(
    "분류 (예: 용돈, 간식, 교통비, 문구류)", key="category_text_input"
)

amount = st.sidebar.number_input(
    "금액 (원)", min_value=0, step=500, key="amount_number_input"
)

note = st.sidebar.text_input(
    "내용 (예: 편의점 빵, 친구 생일선물)", key="note_text_input"
)

# 저장 버튼 클릭 시
if st.sidebar.button("💾 내역 추가 및 저장", key="save_button"):
    if amount > 0 and category.strip() != "":
        real_amount = amount if type_option == "수입 (+)" else -amount

        new_row = pd.DataFrame(
            [{
                "구분": type_option,
                "분류": category.strip(),
                "내용": note.strip(),
                "금액(원)": real_amount,
            }]
        )

        st.session_state.records_df = pd.concat(
            [st.session_state.records_df, new_row], ignore_index=True
        )
        save_data(st.session_state.records_df)

        st.sidebar.success("성공적으로 저장되었습니다!")
        st.rerun()
    else:
        st.sidebar.warning("분류와 금액을 올바르게 입력해주세요.")


# --- 4. 메인 화면: 잔액 및 요약 ---
df = st.session_state.records_df

# 잔액 계산
total_balance = (
    int(df["금액(원)"].sum())
    if not df.empty and "금액(원)" in df.columns
    else 0
)

st.metric(label="💵 현재 남은 돈 (잔액)", value=f"{total_balance:,} 원")

st.write("---")

# --- 5. 거래 내역 출력 및 삭제 기능 ---
st.subheader("📋 전체 거래 내역")

if not df.empty:
    st.dataframe(df, use_container_width=True)

    # 개별 내역 삭제
    st.markdown("#### 🗑️ 특정 내역 삭제하기")
    delete_index = st.number_input(
        "삭제할 내역의 행 번호 (표 맨 왼쪽의 숫자 0, 1, 2...)",
        min_value=0,
        max_value=max(0, len(df) - 1),
        step=1,
        key="delete_index_input",
    )

    if st.button("❌ 선택한 내역 삭제", key="delete_one_button"):
        st.session_state.records_df = (
            st.session_state.records_df.drop(index=delete_index).reset_index(
                drop=True
            )
        )
        save_data(st.session_state.records_df)
        st.success(f"{delete_index}번 내역이 삭제되었습니다!")
        st.rerun()

    st.write("---")

    # 전체 초기화
    with st.expander("⚠️ 전체 내역 초기화 (주의)"):
        st.write("저장된 모든 용돈기입장 데이터를 삭제합니다.")
        if st.button("🚨 전체 데이터 삭제하기", key="delete_all_button"):
            st.session_state.records_df = pd.DataFrame(
                columns=["구분", "분류", "내용", "금액(원)"]
            )
            save_data(st.session_state.records_df)
            st.success("모든 내역이 초기화되었습니다.")
            st.rerun()

    # 지출 차트 시각화
    expense_df = df[df["금액(원)"] < 0].copy()
    if not expense_df.empty:
        expense_df["지출금액"] = expense_df["금액(원)"].abs()

        st.write("---")
        st.subheader("📊 어디에 돈을 제일 많이 썼을까?")
        category_sum = expense_df.groupby("분류")["지출금액"].sum()
        st.bar_chart(category_sum)

else:
    st.info(
        "아직 입력된 내역이 없습니다. 왼쪽 사이드바에서 내역을 추가해 보세요!"
    )