import streamlit as st

# 1. 데이터베이스(테이블 -> 딕셔너리)
personas = {
    "유관순": {"img": "yugwansun.png", "prompt": "다정하지만 강인한 말투. '~해요'체", "content": "1919년 아우내 장터 만세 운동 주도..."},
    "안중근": {"img": "anjunggeun.png", "prompt": "논리적이고 침착한 말투. '~하오'체", "content": "1909년 하얼빈 역 이토 히로부미 처단..."},
    "윤봉길": {"img": "yunbonggil.png", "prompt": "열정적인 행동파 말투. '~합시다'체", "content": "1932년 홍커우 공원 의거 실행..."}
}

st.title("📜 타임톡(Time-Talk)")

# 2. 선택 로직
char_name = st.sidebar.selectbox("인물 선택", list(personas.keys()))
char_data = personas[char_name]

# 3. 답변 생성 함수 (루아의 함수를 파이썬 def로 변환)
def get_ai_response(name, user_input):
    # 데이터 매칭
    info = personas[name]
    # 프롬프트 생성 (f-string 사용)
    return f"[{name}의 답변]: 당신의 질문 '{user_input}'에 대해, {info['prompt']}로 대답합니다. \n\n역사적 사실: {info['content']}"

# 4. 채팅창 출력
if prompt := st.chat_input("질문 입력"):
    response = get_ai_response(char_name, prompt)
    st.chat_message("assistant").markdown(response)
