import streamlit as st
import openai
from dotenv import load_dotenv
import os

# .env 파일에서 OpenAI API 키 로딩
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="자기소개서 작성 도우미", page_icon="📝", layout='centered')

st.title('자기소개서 작성 도우미 📝')

# Google AdSense 코드 삽입
adsense_code = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4792563201867264"
     crossorigin="anonymous"></script>
"""
st.markdown(adsense_code, unsafe_allow_html=True)

st.markdown("""
<font size="4">🔍 **안내**: 이 챗봇은 자기소개서 작성의 참고를 위해 제공됩니다. 
실제 자기소개서 제출 전에는 꼼꼼한 확인과 수정이 필요합니다.</font>
""", unsafe_allow_html=True)

user_input = st.text_area("자기소개서의 초안이나 구체적인 질문을 입력해주세요:", height=200)

if st.button('답변받기'):
    with st.spinner('답변을 생성하는 중...'):
        messages = [
    {"role": "system", "content": "당신은 사용자의 자기소개서에 현실적인 피드백을 제공하며, 자기소개서 예시 몇 가지도 반드시 작성해주고당신이 면접관이라면 합격시킬 것인지 판단해 줘."},
    {"role": "user", "content": user_input}
]


        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=messages
        )
        st.markdown(f"📘 **AI의 답변:** {response['choices'][0]['message']['content']}", unsafe_allow_html=True)
