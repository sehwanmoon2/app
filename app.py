# app.py
import streamlit as st

st.set_page_config(page_title="CO 중독 예후 예측 계산기", layout="centered")
st.title("CO 중독 예후 예측 (COMPASS Score)")

st.markdown("""
이 계산기는 **COMPASS** 점수(0–8점)를 산출합니다.  
- 점수가 높을수록 1개월 후 신경인지 예후가 좋지 않을 위험이 큽니다.
""")

# 1) 사용자 입력
age = st.number_input("나이 (years)", min_value=0, max_value=120, value=30, step=1)
gcs = st.selectbox("초기 GCS 점수", [">= 13", "6 – 12", "<= 5"])
ck  = st.number_input("Creatine Kinase (CK) 레벨 (U/L)", min_value=0, max_value=10000, value=100, step=1)
dwi = st.selectbox("DWI 영상 병변 여부", ["병변 없음", "병변 있음"])

# 2) 점수 계산
#   Age: <45→0, 45-54→1, ≥55→2
if age < 45:
    pts_age = 0
elif age <= 54:
    pts_age = 1
else:
    pts_age = 2

#   GCS: ≥13→0, 6-12→1, ≤5→2
pts_gcs = 0 if gcs == ">= 13" else (1 if gcs == "6 – 12" else 2)

#   CK: <70→0, 70-1243→1, ≥1244→2
if ck < 70:
    pts_ck = 0
elif ck <= 1243:
    pts_ck = 1
else:
    pts_ck = 2

#   DWI: 병변 없음→0, 병변 있음→2
pts_dwi = 0 if dwi == "병변 없음" else 2

total_score = pts_age + pts_gcs + pts_ck + pts_dwi

# 3) 결과 출력
st.subheader(f"▶ COMPASS Total Score: {total_score} / 8")

# (선택) 위험도 분류용 threshold
threshold = st.slider("고위험 기준점수 (Threshold)", min_value=0, max_value=8, value=4)
risk = "🔴 높은 위험" if total_score >= threshold else "🟢 낮은 위험"
st.markdown(f"**위험도 분류**: {risk}")

st.markdown("""
---  
**점수 부여 기준**  
- **Age**: \<45 → 0점, 45–54 → 1점, ≥55 → 2점  
- **GCS**: ≥13 → 0점, 6–12 → 1점, ≤5 → 2점  
- **CK**: \<70 → 0점, 70–1243 → 1점, ≥1244 → 2점  
- **DWI**: 병변 없음 → 0점, 병변 있음 → 2점  
""")
