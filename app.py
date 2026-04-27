import streamlit as st
import json
import os

st.set_page_config(page_title="포켓몬 이미지 퀴즈", page_icon="🐾")
st.title("📸 이미지를 보고 포켓몬 이름을 맞혀보세요!")
st.info("학번: 2022510003  \n이름: 이채린")

@st.cache_data
def load_data():
    with open('data/quiz_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_users():
    if os.path.exists('data/user_data.json'):
        with open('data/user_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open('data/user_data.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

if 'auth_status' not in st.session_state:
    st.session_state.auth_status = False
if 'user_nickname' not in st.session_state:
    st.session_state.user_nickname = ""

users = load_users()

# 사이드바 설정
st.sidebar.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png", width=100)
st.sidebar.markdown("### 🎮 이용 가이드")
st.sidebar.write("1. 닉네임으로 로그인하세요.\n2. 이미지를 보고 이름을 맞히세요.\n3. 당신의 트레이너 등급을 확인하세요!")

if not st.session_state.auth_status:
    st.subheader("로그인 및 계정 생성")
    nickname = st.text_input("닉네임 입력")
    if nickname:
        if nickname in users:
            password = st.text_input("비밀번호 입력", type="password")
            if st.button("로그인"):
                if users[nickname]['password'] == password:
                    st.session_state.auth_status = True
                    st.session_state.user_nickname = nickname
                    st.rerun()
                else:
                    st.error("비밀번호가 틀렸습니다.")
        else:
            st.warning("새로운 닉네임입니다.")
            new_pw = st.text_input("사용할 비밀번호 설정", type="password")
            if st.button("시작하기"):
                if new_pw:
                    users[nickname] = {"password": new_pw, "score": 0, "answers": []}
                    save_users(users)
                    st.session_state.auth_status = True
                    st.session_state.user_nickname = nickname
                    st.rerun()

else:
    st.sidebar.success(f"트레이너: {st.session_state.user_nickname}")
    if st.sidebar.button("로그아웃"):
        st.session_state.auth_status = False
        st.rerun()

    tab1, tab2 = st.tabs(["🔥 퀴즈 시작", "📊 나의 기록"])

    with tab1:
        questions = load_data()
        all_options = [q['name'] for q in questions] # 모든 포켓몬 이름을 선택지로 활용
        
        user_answers = []
        answered_count = 0

        with st.form("pokemon_quiz"):
            for i, q in enumerate(questions):
                st.image(q['url'], width=200)
                # 오답 선택지를 섞어서 보여주기 위해 간단히 리스트 구성
                ans = st.radio(f"위 포켓몬의 이름은? (Q{i+1})", all_options, key=f"q_{i}", index=None, horizontal=True)
                user_answers.append(ans)
                if ans is not None:
                    answered_count += 1
            
            # 진행바 상단 표시
            st.divider()
            progress_val = answered_count / len(questions)
            st.progress(progress_val)
            st.write(f"진행률: {int(progress_val * 100)}%")

            submit = st.form_submit_button("포켓몬 도감 제출")

            if submit:
                if None in user_answers:
                    st.warning("아직 확인하지 못한 포켓몬이 있습니다!")
                else:
                    score = sum([1 for i, a in enumerate(user_answers) if a == questions[i]['name']])
                    users[st.session_state.user_nickname]['score'] = score
                    users[st.session_state.user_nickname]['answers'] = user_answers
                    save_users(users)
                    
                    st.divider()
                    # 점수대별 등급 판정
                    if score == 10:
                        st.snow()
                        st.success(f"🎉 {score}개 정답! 등급: **오박사**")
                        st.write("모든 포켓몬을 파악하셨군요! 진정한 마스터입니다.")
                    elif score >= 7:
                        st.balloons()
                        st.success(f"✨ {score}개 정답! 등급: **포켓몬 덕후**")
                        st.write("대단한 지식입니다! 전문가 수준이시네요.")
                    elif score >= 4:
                        st.info(f"👍 {score}개 정답! 등급: **신참 트레이너**")
                        st.write("기본기가 탄탄하시네요. 조금만 더 공부하면 덕후가 될 수 있어요!")
                    else:
                        st.warning(f"😅 {score}개 정답! 등급: **포린이**")
                        st.write("괜찮아요! 이제부터 알아가면 되죠. 다시 도전해보세요!")

    with tab2:
        st.header("기록 열람실")
        pw_check = st.text_input("비밀번호를 입력하세요", type="password", key="view_auth")
        if st.button("내역 보기"):
            if pw_check == users[st.session_state.user_nickname]['password']:
                data = users[st.session_state.user_nickname]
                st.write(f"### 최근 점수: {data['score']}점")
                if data['answers']:
                    for i, a in enumerate(data['answers']):
                        st.write(f"Q{i+1} 제출: {a}")
            else:
                st.error("비밀번호가 틀립니다.")