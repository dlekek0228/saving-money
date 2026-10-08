import streamlit as st
import pandas as pd

# 1. 앱 제목 설정
st.title("💰 나만의 용돈기입장")

# 2. Session State를 활용해 데이터가 사라지지 않게 저장
if "records" not in st.session_state:
    st.session_state.records = []

# --- 3. 사이드바: 내역 입력 영역 ---
st.sidebar.header("✏️ 내역 추가하기")

# key 값을 각각 다르게 지정해서 중복 에러를 해결했습니다!
type_option = st.sidebar.radio(
    "구분", 
    ["수입 (+)", "지출 (-)"], 
    key="type_option_radio"
)

category = st.sidebar.text_input(
    "분류 (예: 용돈, 간식, 교통비, 문구류)", 
    key="category_text_input"
)

amount = st.sidebar.number_input(
    "금액 (원)", 
    min_value=0, 
    step=500, 
    key="amount_number_input"
)

note = st.sidebar.text_input(
    "내용 (예: 편의점 빵, 친구 생일선물)", 
    key="note_text_input"
)

# 저장 버튼 클릭 시 동작
if st.sidebar.button("บันทึก/저장하기", key="save_button"):
    if amount > 0 and category.strip() != "":
        # 수입은 양수(+), 지출은 음수(-)로 계산
        real_amount = amount if type_option == "수입 (+)" else -amount
        
        # 내역 추가
        st.session_state.records.append({
            "구분": type_option,
            "분류": category,
            "내용": note,
            "금액(원)": real_amount
        })
        st.sidebar.success("저장되었습니다!")
    else:
        st.sidebar.warning("분류와 금액을 올바르게 입력해주세요.")

# --- 4. 메인 화면: 잔액 및 내역 확인 ---
df = pd.DataFrame(st.session_state.records)

# 잔액 계산
total_balance = df["금액(원)"].sum() if not df.empty else 0

# 잔액 및 요약표 표시
st.metric(label="💵 현재 남은 돈 (잔액)", value=f"{total_balance:,} 원")

st.write("---")
st.subheader("📋 전체 거래 내역")

if not df.empty:
    # 내역 표 출력
    st.dataframe(df, use_container_width=True)
    
    # 지출 내역만 모아서 시각화
    expense_df = df[df["금액(원)"] < 0].copy()
    if not expense_df.empty:
        expense_df["지출금액"] = expense_df["금액(원)"].abs()
        
        st.write("---")
        st.subheader("📊 어디에 돈을 제일 많이 썼을까?")
        # 카테고리별 지출 합계 차트
        category_sum = expense_df.groupby("분류")["지출금액"].sum()
        st.bar_chart(category_sum)
else:
    st.info("아직 입력된 내역이 없습니다. 왼쪽 사이드바에서 내역을 추가해 보세요!")