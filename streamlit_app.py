import os
import streamlit as st
import random
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

st.title("🔎 정혀니가 재희를 찾으러 가는길!")

# 세션 상태 초기화
if 'culprit_position' not in st.session_state:
    st.session_state.culprit_position = random.randint(1, 9)
    st.session_state.guesses = 0
    st.session_state.questions = {1: [], 2: [], 3: []}

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

openai_client = OpenAI(
    api_key=api_key
)

# 캐릭터 응답 함수
def get_character_response(character_id, player_question):
    culprit_position = st.session_state.culprit_position
    prompt = f"""
    당신은 탐정 게임의 캐릭터인 일반인 {character_id}입니다.
    플레이어가 재희를 찾기 위해 당신에게 질문을 합니다.
    재희는 1부터 9까지의 위치 중 {culprit_position}번에 있습니다.
    당신은 재희의 위치에 대한 단서를 줄 수 있지만, 직접적으로 위치를 알려주지는 마세요.
    플레이어의 질문에 친절하고 간결하게 답변하세요.

    플레이어의 질문: "{player_question}"
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
        ]
    )
    answer = response.choices[0].message.content
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
    st.error("게임 오버! 재희를 찾지 못했습니다.ㅠㅠ")
