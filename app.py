import streamlit as st

# 1. 지식베이스 (실제로는 JSON 파일에서 불러와서 사용함)
knowledge_base = {
    "유관순": "1919년 3월 1일 아우내 장터 만세 운동을 주도하다 체포되어 서대문형무소에서 순국했습니다.",
    "안중근": "1909년 10월 26일 하얼빈 역에서 이토 히로부미를 처단하여 대한 독립의 의지를 세계에 알렸습니다.",
    "윤봉길": "1932년 4월 29일 홍커우 공원에서 일본 군인들을 향해 도시락 폭탄과 물통 폭탄을 던졌습니다."
}

# 2. 페르소나 설정
personas = {
    "유관순": "다정하고 따뜻하지만, 정의로운 의지를 가진 말투 '~해요'를 사용하세요.",
    "안중근": "논리적이고 침착하며 무게감 있는 말투 '~하오'를 사용하세요.",
    "윤봉길": "뜨거운 열정과 실천적인 리더십 말투 '~합시다!'를 사용하세요."
}

st.title("📜 타임톡(Time-Talk) - 역사 대화 앱")

# 3. 사이드바 캐릭터 선택
char_name = st.sidebar.selectbox("대화할 인물을 선택하세요:", list(knowledge_base.keys()))

# 4. RAG 로직 (검색 증강 생성)
def get_persona_answer(char_name, user_question):
    # 데이터를 검색(Retrieval)
    fact = knowledge_base[char_name]
    # 성격을 주입(Augmentation)
    persona = personas[char_name]
    
    # 프롬프트 구성 (Generation)
    system_prompt = f"당신은 {char_name}입니다. 성격: {persona}. 아래 사실만을 바탕으로 대답하세요. 사실: {fact}"
    
    # [주의] 나중에 여기에 OpenAI API를 연결하면 진짜 인공지능이 됩니다.
    return f"[{char_name}의 답변]\n\n(시스템 프롬프트: {system_prompt})\n\n{fact} 이 일이 제 삶에서 가장 중요한 순간이었어요."

# 5. 채팅창 UI
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("질문을 입력하세요!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = get_persona_answer(char_name, prompt)
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
