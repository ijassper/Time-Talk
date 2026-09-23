import os
import json
import streamlit as st
from openai import OpenAI

# [1. 데이터베이스] - 공공데이터를 딕셔너리로 구조화
knowledge_base = {
    "유관순": {
        "img": "yugwansun.png",
        "fact": "1919년 3월 1일 아우내 장터 만세 운동을 주도하다 일본 헌병대에 체포되었습니다.",
        "url": "https://archive.much.go.kr/archive/publicationRead/InfoDetailInqire.do?publicationId=PLCT_0000000208",
        "persona": "다정하고 따뜻하지만, 정의로운 의지를 가진 말투 '~해요'를 사용하세요."
    },
    "안중근": {
        "img": "anjunggeun.png",
        "fact": "1909년 10월 26일 하얼빈 역에서 이토 히로부미를 처단하여 대한 독립의 의지를 세계에 알렸습니다.",
        "url": "https://archive.much.go.kr/archive/publicationRead/InfoDetailInqire.do?publicationId=PLCT_0000000274",
        "persona": "논리적이고 침착하며 무게감 있는 말투 '~하오'를 사용하세요."
    },
    "윤봉길": {
        "img": "yunbonggil.png",
        "fact": "1932년 4월 29일 홍커우 공원에서 도시락 폭탄과 물통 폭탄을 던져 독립 의지를 증명했습니다.",
        "url": "https://archive.much.go.kr/archive/publicationRead/InfoDetailInqire.do?publicationId=PLCT_0000000274",
        "persona": "뜨거운 열정과 실천적인 리더십 말투 '~합시다!'를 사용하세요."
    }
}

# OpenAI 클라이언트 안전 생성 헬퍼
def get_openai_client():
    api_key = None
    # 1. Streamlit Secrets 우선 설정 확인
    try:
        if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    
    # 2. 시스템 환경 변수 확인
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    
    # 3. 공백 및 은닉 문자/따옴표 제거 (401 인증 오류 방지)
    if api_key and isinstance(api_key, str):
        api_key = api_key.strip().strip('"').strip("'")
        if api_key:
            return OpenAI(api_key=api_key)
    return None

# RAG / 페르소나 답변 생성
def get_persona_answer(char_name, user_question, char_data):
    client = get_openai_client()
    if not client:
        return f"[{char_name}의 답변] : API 키가 설정되지 않았습니다. OpenAI API 키를 등록해주세요."

    system_prompt = f"당신은 {char_name}입니다. {char_data['persona']}"
    context = f"다음은 당신의 삶에 대한 역사적 사실입니다: {char_data['fact']}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"{system_prompt}\n{context}\n답변 시 출처 정보를 하단에 반드시 제공하세요."},
                {"role": "user", "content": user_question}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[{char_name}의 답변] : API 연결 오류가 발생했습니다.: {str(e)}"

# [학생용 자기주도 학습] 역사 퀴즈 자동 생성
def generate_history_quiz(char_name, char_data, history):
    client = get_openai_client()
    if not client:
        return {
            "question": f"{char_name} 의사/열사의 주요 역사적 활동으로 올바른 것은 무엇일까요?",
            "options": [
                char_data["fact"],
                "1945년 광복절 국경일 선포를 주도하였습니다.",
                "훈민정음 언해본 편찬에 참여하였습니다.",
                "1905년 을사늑약 체결을 주도하였습니다."
            ],
            "answer": 0,
            "explanation": f"정답은 1번입니다! {char_data['fact']}"
        }
    
    prompt = f"""
    당신은 역사 교육 전문가이자 {char_name}입니다.
    학생과의 대화 내용과 아래 역사적 사실을 기반으로 학생의 이해도를 확인할 객관식 퀴즈 1문제를 JSON 형식으로 생성하세요.

    [인물 정보]
    인물: {char_name}
    기본 사실: {char_data['fact']}

    [최근 대화 내용]
    {json.dumps(history[-6:], ensure_ascii=False)}

    [반환 JSON 형식을 엄격히 준수하세요]
    {{
        "question": "퀴즈 질문 내용",
        "options": ["보기1", "보기2", "보기3", "보기4"],
        "answer": 0,
        "explanation": "정답 해설"
    }}
    * answer는 0, 1, 2, 3 중 정답 인덱스 정수입니다.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {
            "question": f"{char_name} 의사/열사의 주요 업적으로 올바른 것은 무엇일까요?",
            "options": [
                char_data["fact"],
                "임진왜란에서 한산도 대첩을 이끌었습니다.",
                "팔만대장경을 조판하였습니다.",
                "수원 화성을 성곽으로 축조하였습니다."
            ],
            "answer": 0,
            "explanation": f"정답은 1번입니다! {char_data['fact']}"
        }

# [교사 수업 지원] 수업 활동지 생성
def generate_teacher_worksheet(char_name, char_data, history):
    client = get_openai_client()
    if not client:
        return "⚠️ OpenAI API 키가 설정되지 않아 활동지를 생성할 수 없습니다. API 키를 등록해주세요."

    history_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in history])
    
    prompt = f"""
    당신은 대한민국 역사 교육 전문 교사입니다. 
    학생이 AI 역사 인물 챗봇({char_name})과 나눈 대화 내역을 바탕으로 수업 시간에 바로 활용할 수 있는 [교사용 수업 활동지]를 마크다운 형식으로 생성해주세요.

    [대화 인물]
    인물: {char_name}
    주요 사료: {char_data['fact']}

    [대화 히스토리]
    {history_str}

    [반드시 다음 마크다운 구조로 작성하세요]
    # 📜 [{char_name} 의사/열사 연계 역사 탐구 수업 활동지]

    ## 🎯 1. 수업 목표 및 핵심 주제
    - (대화 내용을 반영한 수업 목표 2가지)

    ## 💬 2. 초/중/고 수준별 역사 토론 주제
    - **초등 학생용**: (토론 주제 및 가이드 질문)
    - **중등 학생용**: (토론 주제 및 가이드 질문)
    - **고등 학생용**: (토론 주제 및 가이드 질문)

    ## 📝 3. 대화 기반 빈칸 채우기 퀴즈
    1. (문장 내 ___ 빈칸 포함 문제 1)
    2. (문장 내 ___ 빈칸 포함 문제 2)
    3. (문장 내 ___ 빈칸 포함 문제 3)

    ### [정답 및 해설]
    1. 정답: ... (해설)
    2. 정답: ... (해설)
    3. 정답: ... (해설)

    ## 💡 4. 교사용 수업 지도 팁
    - (대한민국역사박물관 오픈아카이브 오픈데이터 활용법 및 수업 유의점)
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"활동지 생성 중 오류가 발생했습니다: {str(e)}"


# [2. UI 설정 및 세션 초기화]
st.set_page_config(page_title="타임톡(Time-Talk)", page_icon="📜", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "badges" not in st.session_state:
    st.session_state.badges = []
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "worksheet_content" not in st.session_state:
    st.session_state.worksheet_content = None

# [사이드바 UI]
st.sidebar.title("📜 타임톡 메뉴")

# 사이드바 인물 선택
char_name = st.sidebar.selectbox("대화할 인물을 선택하세요:", list(knowledge_base.keys()))
char_data = knowledge_base[char_name]

# 사이드바 🏆 학습 배지 보관함
st.sidebar.divider()
st.sidebar.subheader("🏆 나의 학습 배지")
if st.session_state.badges:
    for badge in set(st.session_state.badges):
        st.sidebar.success(f"**{badge}**")
else:
    st.sidebar.info("대화를 5턴 이상 진행하고 역사 퀴즈를 맞히면 **'🏅 역사 탐험가 배지'**가 수여됩니다!")

# 사이드바 👩‍🏫 교사 수업 지원
st.sidebar.divider()
st.sidebar.subheader("👩‍🏫 교사 수업 지원")
if st.sidebar.button("📜 교사용 수업 활동지 생성하기", use_container_width=True):
    if not st.session_state.messages:
        st.sidebar.warning("대화 내역이 없습니다. 먼저 인물과 대화를 진행해주세요.")
    else:
        with st.spinner("학생 대화 기반 수업 활동지를 자동 작성 중입니다..."):
            worksheet = generate_teacher_worksheet(char_name, char_data, st.session_state.messages)
            st.session_state.worksheet_content = worksheet
            st.sidebar.success("수업 활동지가 생성되었습니다!")

if st.session_state.worksheet_content:
    st.sidebar.download_button(
        label="📥 활동지 다운로드 (.md)",
        data=st.session_state.worksheet_content,
        file_name=f"{char_name}_수업활동지.md",
        mime="text/markdown",
        use_container_width=True
    )

# [메인 UI]
st.title("📜 타임톡(Time-Talk)")
st.caption("대한민국역사박물관 오픈아카이브 데이터 기반 AI 역사 인물 페르소나 챗봇")

col1, col2 = st.columns([1, 2])
with col1:
    try:
        st.image(char_data["img"], use_container_width=True)
    except Exception:
        st.warning("이미지 파일을 확인하세요.")
with col2:
    st.write(f"### {char_name} 의사/열사")
    st.info(f"**학습 페르소나:** {char_data['persona']}")
    
    # 배지 획득 현황 표시
    if st.session_state.badges:
        st.markdown(" ".join([f"`{b}`" for b in set(st.session_state.badges)]))

# [3. 대화 로직 및 턴 관리]
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("역사에 대해 궁금한 점을 질문해보세요!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_text = get_persona_answer(char_name, prompt, char_data)
        full_response = response_text + f"\n\n🔗 [근거 자료 확인하기]({char_data['url']})"
        st.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# [4. 학생용 자기주도 학습: 5턴 이상 대화 시 역사 퀴즈 출제]
user_turn_count = len([m for m in st.session_state.messages if m["role"] == "user"])

if user_turn_count >= 5:
    st.divider()
    st.subheader("🎯 자기주도 학습: 독립운동가 역사 퀴즈")
    st.caption(f"현재 대화 턴 수: {user_turn_count}턴 달성! 대화 내용을 바탕으로 퀴즈에 도전해보세요.")

    if not st.session_state.quiz_active and not st.session_state.quiz_submitted:
        if st.button("🧩 역사 퀴즈 풀어보기", type="primary"):
            with st.spinner("독립운동가가 출제하는 퀴즈를 생성하고 있습니다..."):
                st.session_state.quiz_data = generate_history_quiz(char_name, char_data, st.session_state.messages)
                st.session_state.quiz_active = True
                st.rerun()

    if st.session_state.quiz_active and st.session_state.quiz_data:
        quiz = st.session_state.quiz_data
        st.info(f"**[질문] {quiz.get('question', '')}**")
        
        with st.form("quiz_form"):
            user_choice = st.radio("정답을 선택하세요:", quiz.get("options", []), key="quiz_options")
            submit_quiz = st.form_submit_button("정답 제출하기")
            
            if submit_quiz:
                options = quiz.get("options", [])
                correct_idx = quiz.get("answer", 0)
                if options and options.index(user_choice) == correct_idx:
                    st.balloons()
                    badge_name = "🏅 역사 탐험가 배지"
                    if badge_name not in st.session_state.badges:
                        st.session_state.badges.append(badge_name)
                    st.success(f"🎉 **정답입니다!** **'{badge_name}'**를 성공적으로 획득하셨습니다!")
                    st.info(f"📖 **해설:** {quiz.get('explanation', '')}")
                    st.session_state.quiz_submitted = True
                    st.session_state.quiz_active = False
                else:
                    st.error("❌ 아쉽습니다. 다시 정답을 고민하고 도전해보세요!")
                    if quiz.get("explanation"):
                        st.caption(f"💡 힌트: {quiz.get('explanation')}")

    if st.session_state.quiz_submitted:
        st.success("✅ **이번 대화 세션의 퀴즈를 완료하셨습니다!** 사이드바에서 획득한 **'🏅 역사 탐험가 배지'**를 확인해보세요.")

# [5. 교사 수업 지원: 생성된 수업 활동지 미리보기]
if st.session_state.worksheet_content:
    st.divider()
    with st.expander("📄 [교사용 수업 활동지 미리보기]", expanded=True):
        st.markdown(st.session_state.worksheet_content)
