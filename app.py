import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="나만의 AI 영단어장", page_icon="📚", layout="centered")

st.title("📚 나만의 AI 영단어장 & 퀴즈")
st.caption("영단어를 입력하면 AI가 뜻, 영영풀이, 예문, 퀴즈를 자동으로 만들어 줍니다!")

# API 키 입력창 (사이드바)
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("Gemini API Key를 입력하세요:", type="password")
    st.markdown("[API Key 발급받기](https://aistudio.google.com/)")

if not api_key:
    st.warning("👈 왼쪽 사이드바에 Gemini API Key를 입력해주세요!")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# 세션 상태 초기화 (단어 저장용)
if "words" not in st.session_state:
    st.session_state.words = []

# 탭 생성
tab1, tab2, tab3 = st.tabs(["➕ 단어 추가", "🗂️ 단어장 보기", "✏️ 복습 퀴즈"])

# --- 탭 1: 단어 추가 ---
with tab1:
    st.subheader("새로운 영단어 추가하기")
    new_word = st.text_input("공부하고 싶은 영단어를 입력하세요 (예: resilience):")
    
    if st.button("AI 분석 및 단어장에 추가", type="primary"):
        if new_word:
            with st.spinner("AI가 단어를 분석 중입니다..."):
                prompt = f"""
                영단어 '{new_word}'에 대해 아래 JSON 형식으로 응답해줘. 다른 설명 없이 오직 JSON만 반환해.
                {{
                    "word": "{new_word}",
                    "pronunciation": "발음기호",
                    "part_of_speech": "품사",
                    "meaning": "한글 뜻",
                    "definition": "영영풀이",
                    "example": "영어 예문",
                    "example_ko": "예문 한글 번역",
                    "quiz_question": "예문에서 해당 단어를 ___ 로 비운 문장",
                    "quiz_options": ["정답단어", "오답1", "오답2", "오답3"]
                }}
                """
                try:
                    response = model.generate_content(prompt)
                    text = response.text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(text)
                    
                    st.session_state.words.append(data)
                    st.success(f"'{new_word}' 단어가 성공적으로 추가되었습니다!")
                    st.json(data)
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
        else:
            st.warning("단어를 입력해주세요.")

# --- 탭 2: 단어장 보기 ---
with tab2:
    st.subheader("나만의 단어장")
    if not st.session_state.words:
        st.info("아직 추가된 단어가 없습니다. '단어 추가' 탭에서 단어를 등록해 보세요!")
    else:
        for idx, item in enumerate(st.session_state.words, 1):
            with st.expander(f"📌 {idx}. {item['word']} [{item.get('pronunciation', '')}] - {item['meaning']}"):
                st.write(f"**품사:** {item.get('part_of_speech', '')}")
                st.write(f"**영영풀이:** {item['definition']}")
                st.write(f"**예문:** {item['example']}")
                st.write(f"*(번역: {item['example_ko']})*")

# --- 탭 3: 복습 퀴즈 ---
with tab3:
    st.subheader("빈칸 채우기 퀴즈")
    if len(st.session_state.words) == 0:
        st.info("퀴즈를 풀려면 먼저 단어를 추가해 주세요!")
    else:
        score = 0
        for idx, item in enumerate(st.session_state.words):
            st.markdown(f"**Q{idx+1}. 다음 빈칸에 들어갈 알맞은 단어는?**")
            st.write(f"👉 {item['quiz_question']}")
            st.write(f"*(뜻: {item['meaning']})*")
            
            user_choice = st.radio(
                f"정답을 선택하세요 ({item['word']}):",
                options=item['quiz_options'],
                key=f"quiz_{idx}"
            )
            
            if user_choice == item['word']:
                st.success("⭕ 정답입니다!")
                score += 1
            else:
                st.error(f"❌ 틀렸습니다. 정답은 **{item['word']}** 입니다.")
            st.divider()
            
        st.metric(label="최종 점수", value=f"{score} / {len(st.session_state.words)}")
