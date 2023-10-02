import streamlit as st
import openai
from dotenv import load_dotenv
import os

# .env 파일에서 OpenAI API 키 로딩
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def get_feedback_and_examples(user_title, user_content):
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct-0914",
        prompt=f"사용자의 자기소개서 내용을 기반으로 구체적인 피드백과 해당 피드백을 바탕으로 한 개선 예시를 제공해주세요. 피드백과 예시는 명확하게 구분해주세요. 내용: {user_content}."

,
        max_tokens=2000,
        temperature=0.01,
        top_p=1
    )
    
    text = response.choices[0].text.strip()
    
    # "개선"이라는 키워드가 언급된 횟수를 계산합니다.
    improvement_count = text.lower().count("개선")

    # 개선사항이 하나도 없을 경우 예시 부분을 제거합니다.
    if improvement_count < 1:
        index_example_start = text.lower().find("예시:")
        if index_example_start != -1:
            text = text[:index_example_start].strip()

    # 피드백의 중요도에 따라 합격 여부를 판단합니다.
    if "문제" in text or "개선" in text:
        verdict = "🔴 합격 여부: 불합격 (자기소개서에 개선이 필요합니다.)"
    else:
        verdict = "🟢 합격 여부: 합격 가능"

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
    st.write("⚠️ 자기소개서 제목과 내용 합쳐서 2000자 이내로 작성해주세요!")

submit_button = st.button('답변받기')

if submit_button:
    with st.spinner('답변 생성 중...'):
        feedback, verdict = get_feedback_and_examples(user_title, user_content)
    st.markdown(feedback, unsafe_allow_html=True)
    st.markdown(verdict, unsafe_allow_html=True)
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

