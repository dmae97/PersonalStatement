import base64
from io import BytesIO
import qrcode
import streamlit as st
import openai
from dotenv import load_dotenv
import os

# .env 파일에서 OpenAI API 키 로딩
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Streamlit 앱 제목 설정
st.set_page_config(page_title="자기소개서 작성 도우미", page_icon="📝", layout='centered')

# 사이드바를 이용한 정보 표시
st.sidebar.title("멘토 챗봇 Q&A")
st.sidebar.info("짧은 질문에 대한 답변을 얻을 수 있습니다.")

sidebar_question = st.sidebar.text_input("질문을 입력해주세요:")
if sidebar_question:
    response_sidebar = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=sidebar_question,
        max_tokens=2000
    )
    st.sidebar.markdown(f"**답변:** {response_sidebar.choices[0].text.strip()}")

# 메인 제목
st.title('자기소개서 작성 도우미 📝')

# 사용자에게 안내 사항 전달
st.markdown("""
<font size="4">🔍 **안내**: 이 챗봇은 자기소개서 작성의 참고를 위해 제공됩니다. 
실제 자기소개서 제출 전에는 꼼꼼한 확인과 수정이 필요합니다.</font>
""", unsafe_allow_html=True)

# 사용자 입력
user_input = st.text_area("자기소개서의 초안이나 구체적인 질문을 입력해주세요:", height=200)

# 답변 받기 버튼
if st.button('답변받기'):
    with st.spinner('답변을 생성하는 중...'):
        # 사용자의 입력을 특정 프롬프트와 함께 구성하여 AI에 명확한 지시를 전달
        prompt_text = f"다음은 자기소개서 작성에 관한 사용자의 질문입니다: '{user_input}'. 이에 대한 구체적인 조언과 수정 제안을 해주세요."

        # `openai.Completion`을 사용하여 응답 받기
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt_text,
            max_tokens=2000
        )

        # 결과를 스트림릿에 출력
        st.markdown(
            f"📘 **AI의 답변:** {response.choices[0].text.strip()}", unsafe_allow_html=True)


# ... 기존 코드 ...

# 비트코인 주소를 위한 QR 코드 생성
bitcoin_address = "3CMCKgTMcLsz4mMC4veBREio3YzppVeXGP"
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(bitcoin_address)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")

# 이미지를 스트림릿에 표시할 수 있도록 변환
buf = BytesIO()
img.save(buf, format="PNG")
image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

st.write(f"""
### 도네이션 받기

이 서비스가 도움이 되었다면, 아래의 비트코인 주소나 QR 코드를 통해 도네이션을 고려해주세요:

비트코인 주소: `{bitcoin_address}`

![QR Code](data:image/png;base64,{image_base64})

""", unsafe_allow_html=True)
