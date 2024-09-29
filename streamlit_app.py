import streamlit as st
import random
from openai import OpenAI

#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

# 사이드바에 OpenAI API 키 입력받기
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    st.markdown("[OpenAI API 키 받기](https://platform.openai.com/account/api-keys)")

st.title("🔎 재희를 찾아라!")

# 세션 상태 초기화
if 'culprit_position' not in st.session_state:
    st.session_state.culprit_position = random.randint(1, 9)
    st.session_state.guesses = 0
    st.session_state.questions = {1: [], 2: [], 3: []}

# OpenAI API 키 설정
if openai_api_key:
    OpenAI.api_key = openai_api_key
else:
    st.warning("OpenAI API 키를 입력하세요.")
    st.stop()

# 3x3 그리드 생성
positions = []
for i in range(3):
    cols = st.columns(3)
    for j in range(3):
        pos = i * 3 + j + 1
        with cols[j]:
            if st.button(f"🔲 위치 {pos}", key=f"pos{pos}"):
                if st.session_state.guesses < 2:
                    st.session_state.guesses += 1
                    if pos == st.session_state.culprit_position:
                        st.success("🎉 재희를 찾았습니다!")
                    else:
                        st.error("😢 재희가 없습니다.")
                else:
                    st.warning("❗ 시도 횟수를 모두 사용하셨습니다.")
            positions.append(pos)

st.write(f"🕵️‍♂️ 남은 시도 횟수: {2 - st.session_state.guesses}번")

openai_client = OpenAI()

# 캐릭터 응답 함수
def get_character_response(character_id, player_question):
    culprit_position = st.session_state.culprit_position
    prompt = f"""
    당신은 탐정 게임의 캐릭터인 일반인 {character_id}입니다.
    플레이어가 범인을 찾기 위해 당신에게 질문을 합니다.
    범인은 1부터 9까지의 위치 중 {culprit_position}번에 있습니다.
    당신은 범인의 위치에 대한 단서를 줄 수 있지만, 직접적으로 위치를 알려주지는 마세요.
    플레이어의 질문에 친절하고 간결하게 답변하세요.

    플레이어의 질문: "{player_question}"
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
        ]
    )
    answer = response.choices[0].message
    return answer

# 일반인들에게 질문하기
st.header("💬 일반인들에게 질문하기")
for i in range(1, 4):
    if len(st.session_state.questions[i]) < 2:
        with st.expander(f"일반인 {i}에게 질문하기"):
            question = st.text_input(f"일반인 {i}에게 질문하세요:", key=f"question_{i}_{len(st.session_state.questions[i])}")
            if question:
                # 질문 저장
                st.session_state.questions[i].append({"question": question})
                # 응답 생성
                answer = get_character_response(i, question)
                st.session_state.questions[i][-1]["answer"] = answer
                st.write(f"**일반인 {i}**: {answer}")
    else:
        st.write(f"🛑 일반인 {i}에게 더 이상 질문할 수 없습니다.")

# 게임 종료 확인
if st.session_state.guesses >= 2 and st.session_state.culprit_position != pos:
    st.error("게임 오버! 범인을 찾지 못했습니다.")
