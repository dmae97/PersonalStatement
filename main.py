import streamlit as st
import openai
import json
import os
from dotenv import load_dotenv
import streamlit as st


# Load OpenAI API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


# Function to get feedback and examples

def get_feedback_and_examples(user_title, user_content):
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct-0914",
        prompt=f"사용자의 자기소개서 내용을 기반으로 구체적인 피드백과 해당 피드백을 바탕으로 한 개선 예시를 제공해주세요. 피드백과 예시는 명확하게 구분해주세요. 내용: {user_content}.",
        max_tokens=2000,
        temperature=0.01,
        top_p=0.1
    )
    
    text = response.choices[0].text.strip()

    def contains_weird_characters(text):
        weird_characters = ['ㅋ', 'ㅎ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅉ', 'ㅊ', 'ㅈ', 'ㅌ', 'ㄷ', 'ㄸ', 'ㄲ', 'ㄱ', 'ㄴ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅆ', 'ㅅ', 'ㅇ', 'ㅛ', 'ㅕ', 'ㅑ', 'ㅐ', 'ㅔ', 'ㅓ', 'ㅏ', 'ㅣ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅟ', 'ㅞ', 'ㅝ', 'ㅢ', 'ㅡ']
        for char in weird_characters:
            if char in text:
                return True
        return False

    if "문제" in text or "개선" in text or "이상한단어" in text or "구체적" in text or "알수없는 문자" in text or "부족" in text or contains_weird_characters(text):
        verdict = "🔴 합격 여부: 불합격 (자기소개서에 개선이 필요합니다.)"
    else:
        verdict = "🟢 합격 여부: 합격 가능(정확하지 않을수 있습니다)"

    return text, verdict



# Streamlit UI
st.title('자기소개서 작성 도우미 📝')

# 제목 입력창
user_title = st.text_area("자기소개서 제목을 입력해주세요:", placeholder="ex) 지원동기", key="user_title_key")

# 내용 입력창
user_content = st.text_area("자기소개서 내용을 2000자 이내로 입력해주세요:", 
                            placeholder="ex) 돈 벌기 위해 지원하게 됐는데요...",
                            height=300, key="user_content_key")

char_count = len(user_title) + len(user_content)
st.write(f"입력한 글자 수: {char_count}/2000")

if char_count > 2000:
    st.warning("⚠️ 자기소개서 제목과 내용 합쳐서 2000자 이내로 작성해주세요!")

submit_button = st.button('답변받기')

if submit_button:
    with st.spinner('답변 생성 중...'):
        feedback, verdict = get_feedback_and_examples(user_title, user_content)
    st.markdown(feedback, unsafe_allow_html=True)
    st.markdown(verdict, unsafe_allow_html=True)

# 사이드바
import streamlit as st
import openai
import json

with st.sidebar.form(key='ask_question'):
    question = st.text_input('질문:')
    submit_question = st.form_submit_button('질문하기')

    if submit_question and question:
        # OpenAI API를 사용하여 질문에 대한 답변을 생성합니다.
        messages = [
            {"role": "system", "content": "이 웹사이트는 자기소개서 작성을 도와주는 사이트입니다. 그리고 질문의 답변을 매우 매우 짧고 간단 하게 100자 이내에 대답해주세요."},
            {"role": "user", "content": question}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        answer = response.choices[0].message['content'].strip()

        # 답변을 사이드바에 표시합니다.
        st.sidebar.markdown('**답변:**')
        st.sidebar.markdown(answer)

# 사이드바에 한 줄 게시판 기능 추가
def load_oneline_messages():
    try:
        with open('oneline_messages.json', 'r') as f:
            messages = json.load(f)
            # 각 메시지에 "likes" 키가 있는지 확인
            for message in messages:
                if "likes" not in message:
                    message["likes"] = 0
            return messages
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_oneline_message(message):
    messages = load_oneline_messages()
    messages.append({"content": message, "likes": 0})
    with open('oneline_messages.json', 'w') as f:
        json.dump(messages, f)

def increase_like(index):
    messages = load_oneline_messages()
    messages[index]["likes"] += 1
    with open('oneline_messages.json', 'w') as f:
        json.dump(messages, f)

st.sidebar.header('한 줄 게시판')
with st.sidebar.form(key='oneline_board_form'):
    message = st.text_area("여기에 메시지를 남겨주세요:", max_chars=100)
    if st.form_submit_button('남기기'):
        save_oneline_message(message)
        st.sidebar.success("메시지가 게시판에 저장되었습니다!")
# 관리자 비밀번호 설정 (실제로 사용할 때는 이 비밀번호를 안전하게 관리하세요!)
ADMIN_PASSWORD = "Dmae!@1997"

def delete_oneline_message(index):
    messages = load_oneline_messages()
    del messages[index]  # 지정된 인덱스의 메시지를 삭제
    with open('oneline_messages.json', 'w') as f:
        json.dump(messages, f)  
# 저장된 메시지들을 사이드바에 출력
oneline_messages = load_oneline_messages()
for index, message_data in enumerate(oneline_messages):
    message = message_data["content"]
    likes = message_data.get("likes", 0)  # 이 부분을 수정
    
    st.sidebar.write(message)
    if st.sidebar.button(f'❤️ {likes}', key=f"like_{index}"):
        increase_like(index)
        st.experimental_rerun()

    if st.sidebar.button("Delete", key=f"delete_{index}"):
        password = st.sidebar.text_input("Enter admin password:", type="password")
        if password == ADMIN_PASSWORD:
            delete_oneline_message(index)
            st.sidebar.success("Message deleted!")
            st.experimental_rerun()
        else:
            st.sidebar.warning("Incorrect password!")

    st.sidebar.write("---")   
    
    
    
# Insert the donation button at the desired location
donation_link = "https://toss.me/dmae97/5000"
st.markdown(f'''
<a href="{donation_link}" target="_blank">
<button style="
    background: linear-gradient(to right, #FF4500, #FF6347);
    color:white;
    padding:10px 20px;
    font-size:16px;
    border:none;
    cursor:pointer;
    border-radius: 20px;
    box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease 0s;
    text-align: center;
    align-items: center;
    justify-content: center;
    outline: none;
    width: 300x;
    height: 50x;"
    onmouseover="this.style.boxShadow='0px 15px 20px rgba(46, 229, 157, 0.4)'; this.style.backgroundColor='#FF6347'; this.style.transform='translateY(-7px)'"
    onmouseout="this.style.boxShadow='0px 8px 15px rgba(0, 0, 0, 0.1)'; this.style.backgroundColor='#FF4500'; this.style.transform='translateY(0px)'">
    서비스가 도움이 되셨다면, 작은 응원 부탁드립니다!
</button></a>''', unsafe_allow_html=True)


