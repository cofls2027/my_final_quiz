import streamlit as st
import json
import os

st.set_page_config(page_title="포켓몬 주관식 퀴즈", page_icon="🐾", layout="wide")

st.markdown("""
    <style>
    .fixed-prog-container {
        position: fixed;
        right: 20px;
        top: 15%;
        height: 70%;
        width: 15px;
        background-color: #f0f2f6;
        border-radius: 10px;
        z-index: 999;
    }
    .fixed-prog-bar {
        width: 100%;
        background-color: #ff4b4b;
        border-radius: 10px;
        transition: height 0.5s ease;
        position: absolute;
        bottom: 0;
    }
    .prog-text {
        position: fixed;
        right: 45px;
        top: 45%;
        transform: rotate(90deg);
        font-weight: bold;
        color: #ff4b4b;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        with open('data/quiz_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"name": "피카츄", "url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"}]

def load_users():
    if os.path.exists('data/user_data.json'):
        with open('data/user_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    if not os.path.exists('data'):
        os.makedirs('data')
    with open('data/user_data.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

if 'auth_status' not in st.session_state:
    st.session_state.auth_status = False
if 'user_nickname' not in st.session_state:
    st.session_state.user_nickname = ""

users = load_users()

st.title("🏆 포켓몬 주관식 이름 맞히기")
st.info("학번: 2022510003 \n이름: 이채린")

st.sidebar.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png", width=100)
st.sidebar.markdown("### 🎮 트레이너 센터")

if not st.session_state.auth_status:
    st.subheader("🎮 모험을 시작하기 전!")
    st.info("원하는 닉네임과 비밀번호를 설정하세요!") 

    nickname = st.text_input("닉네임 입력")
    
    if nickname:
        if nickname in users:
            password = st.text_input("비밀번호 입력", type="password")
            if st.button("로그인"):
                print(f"[EC2 로그] '{nickname}' 트레이너가 로그인 버튼을 클릭했습니다!") 
                
                if users[nickname]['password'] == password:
                    st.session_state.auth_status = True
                    st.session_state.user_nickname = nickname
                    st.rerun()
                else:
                    st.error("비밀번호가 틀렸습니다.")
        else:
            st.warning(f"'{nickname}'(은)는 새로운 트레이너 닉네임입니다.")
            new_pw = st.text_input("사용할 비밀번호 설정", type="password")
            if st.button("모험 시작"):
                print(f"[EC2 로그] 새로운 트레이너 '{nickname}'님이 모험 시작(가입) 버튼을 클릭했습니다!")
                
                if new_pw:
                    users[nickname] = {"password": new_pw, "score": 0, "answers": []}
                    save_users(users)
                    st.session_state.auth_status = True
                    st.session_state.user_nickname = nickname
                    st.rerun()
                else:
                    st.error("비밀번호를 입력해 주세요!")

else:
    st.sidebar.success(f"트레이너: {st.session_state.user_nickname}")
    if st.sidebar.button("로그아웃"):
        print(f"[EC2 로그] '{st.session_state.user_nickname}' 트레이너가 로그아웃했습니다.")
        st.session_state.auth_status = False
        st.rerun()

    tab1, tab2 = st.tabs(["🔥 퀴즈 도전", "📊 기록실"])

    with tab1:
        questions = load_data()
        user_answers = []
        answered_count = 0

        st.subheader("이미지를 보고 포켓몬의 이름을 정확히 입력하세요!")
        
        for i, q in enumerate(questions):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(q['url'], width=150)
            with col2:
                ans = st.text_input(f"Q{i+1} 포켓몬 이름은?", key=f"q_{i}").strip()
                user_answers.append(ans)
                if ans != "":
                    answered_count += 1
            st.divider()

        progress_percent = (answered_count / len(questions)) * 100
        st.markdown(f"""
            <div class="fixed-prog-container">
                <div class="fixed-prog-bar" style="height: {progress_percent}%;"></div>
            </div>
            <div class="prog-text">진행률 {int(progress_percent)}%</div>
            """, unsafe_allow_html=True)

        if st.button("모든 답안 제출하기"):
            print(f"[EC2 로그] '{st.session_state.user_nickname}'님이 퀴즈 답안 제출 버튼을 클릭했습니다!")
            
            if "" in user_answers:
                st.warning("아직 풀지 않은 문제가 있습니다!")
            else:
                score = sum([1 for i, a in enumerate(user_answers) if a == questions[i]['name']])
                users[st.session_state.user_nickname]['score'] = score
                users[st.session_state.user_nickname]['answers'] = user_answers
                save_users(users)

                if score == len(questions):
                    st.snow()
                    st.success(f"🏆 {score}/{len(questions)} - 등급: **오박사**")
                elif score >= 7:
                    st.balloons()
                    st.success(f"✨ {score}/{len(questions)} - 등급: **포켓몬 덕후**")
                elif score >= 4:
                    st.info(f"👍 {score}/{len(questions)} - 등급: **신참 트레이너**")
                else:
                    st.warning(f"😅 {score}/{len(questions)} - 등급: **포린이**")

    with tab2:
        st.header("나의 모험 기록")
        pw_check = st.text_input("본인 확인 (비밀번호)", type="password", key="history_pw")
        if st.button("기록 열람"):
            print(f"[EC2 로그] '{st.session_state.user_nickname}'님이 기록 열람 버튼을 클릭했습니다!")
            
            if pw_check == users[st.session_state.user_nickname]['password']:
                rec = users[st.session_state.user_nickname]
                st.write(f"### 최종 점수: {rec.get('score', 0)}점")
                for i, a in enumerate(rec.get('answers', [])):
                    st.write(f"Q{i+1} 제출 답안: {a}")
            else:
                st.error("비밀번호가 일치하지 않습니다.")