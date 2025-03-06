import streamlit as st
import openai
from openai import OpenAI
import google.generativeai as genai
import anthropic
import json
import os
from dotenv import load_dotenv
import time
import re
from typing import Dict, List, Optional, Union, Any
import uuid
import base64
from io import BytesIO
from PIL import Image
import requests

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="AI Model Playground",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .main-header {
        font-family: 'Roboto', sans-serif;
        color: #1E88E5;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
        border-bottom: 2px solid #e0e0e0;
    }
    
    /* Card styling */
    .stCard {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1rem;
        background-color: white;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 20px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Input field styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #f1f3f4;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        background-color: #f1f3f4;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5 !important;
        color: white !important;
    }
    
    /* Chat container */
    .chat-container {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        height: 400px;
        overflow-y: auto;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    
    /* Chat message */
    .user-message {
        background-color: #DCF8C6;
        padding: 10px 15px;
        border-radius: 15px 15px 0 15px;
        margin: 5px 0;
        max-width: 80%;
        align-self: flex-end;
        margin-left: auto;
    }
    
    .bot-message {
        background-color: #FFFFFF;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 0;
        margin: 5px 0;
        max-width: 80%;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    /* Model selection card */
    .model-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .model-card:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .selected-model {
        border: 2px solid #1E88E5;
        background-color: #E3F2FD;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 1rem 0;
        margin-top: 2rem;
        border-top: 1px solid #e0e0e0;
        font-size: 0.8rem;
        color: #757575;
    }
    
    /* Loading animation */
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 1rem 0;
    }
    
    /* Code block styling */
    pre {
        background-color: #f1f3f4;
        padding: 1rem;
        border-radius: 5px;
        overflow-x: auto;
    }
    
    code {
        font-family: 'Courier New', monospace;
    }
    
    /* Image styling */
    .generated-image {
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {
        'openai': '',
        'google': '',
        'anthropic': '',
    }
if 'current_model' not in st.session_state:
    st.session_state.current_model = 'openai/gpt-3.5-turbo'
if 'temperature' not in st.session_state:
    st.session_state.temperature = 0.7
if 'max_tokens' not in st.session_state:
    st.session_state.max_tokens = 1000

# Helper functions
def get_model_provider(model_name: str) -> str:
    """Extract provider from model name."""
    return model_name.split('/')[0]

def format_message(message: str, is_user: bool) -> str:
    """Format message with appropriate styling."""
    if is_user:
        return f'<div class="user-message">{message}</div>'
    else:
        return f'<div class="bot-message">{message}</div>'

def display_chat_history():
    """Display chat history with styling."""
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.chat_history:
            st.markdown(
                format_message(message['content'], message['is_user']),
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

def generate_response(prompt: str, model: str, temperature: float, max_tokens: int) -> str:
    """Generate response from selected AI model."""
    provider = get_model_provider(model)
    model_name = model.split('/')[1]
    
    try:
        if provider == 'openai':
            if not st.session_state.api_keys['openai']:
                return "⚠️ OpenAI API key is not set. Please add your API key in the sidebar."
            
            client = OpenAI(api_key=st.session_state.api_keys['openai'])
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
            
        elif provider == 'google':
            if not st.session_state.api_keys['google']:
                return "⚠️ Google API key is not set. Please add your API key in the sidebar."
            
            genai.configure(api_key=st.session_state.api_keys['google'])
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
            
        elif provider == 'anthropic':
            if not st.session_state.api_keys['anthropic']:
                return "⚠️ Anthropic API key is not set. Please add your API key in the sidebar."
            
            client = anthropic.Anthropic(api_key=st.session_state.api_keys['anthropic'])
            message = client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
            
        else:
            return f"Provider {provider} is not supported."
    except Exception as e:
        return f"Error: {str(e)}"

# Sidebar for API keys and settings
with st.sidebar:
    st.markdown('<h2 style="text-align: center;">⚙️ Settings</h2>', unsafe_allow_html=True)
    
    with st.expander("API Keys", expanded=True):
        st.session_state.api_keys['openai'] = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.api_keys['openai'],
            help="Enter your OpenAI API key"
        )
        
        st.session_state.api_keys['google'] = st.text_input(
            "Google AI API Key",
            type="password",
            value=st.session_state.api_keys['google'],
            help="Enter your Google AI API key"
        )
        
        st.session_state.api_keys['anthropic'] = st.text_input(
            "Anthropic API Key",
            type="password",
            value=st.session_state.api_keys['anthropic'],
            help="Enter your Anthropic API key"
        )
    
    with st.expander("Model Settings", expanded=True):
        st.session_state.temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.temperature,
            step=0.1,
            help="Higher values make output more random, lower values more deterministic"
        )
        
        st.session_state.max_tokens = st.slider(
            "Max Tokens",
            min_value=100,
            max_value=4000,
            value=st.session_state.max_tokens,
            step=100,
            help="Maximum number of tokens to generate"
        )
    
    st.markdown("---")
    st.markdown(
        """
        <div class="footer">
            <p>Made with ❤️ by AI Enthusiasts</p>
            <p>© 2024 AI Model Playground</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Main content
st.markdown('<h1 class="main-header">🤖 AI Model Playground</h1>', unsafe_allow_html=True)

# Model selection
st.markdown('<h3>Select AI Model</h3>', unsafe_allow_html=True)

# Create columns for model selection cards
col1, col2, col3 = st.columns(3)

with col1:
    openai_selected = st.session_state.current_model.startswith('openai')
    openai_class = "model-card selected-model" if openai_selected else "model-card"
    
    st.markdown(f'<div class="{openai_class}">', unsafe_allow_html=True)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/OpenAI_Logo.svg/1024px-OpenAI_Logo.svg.png", width=100)
    st.markdown("<h4>OpenAI Models</h4>", unsafe_allow_html=True)
    openai_model = st.selectbox(
        "Select OpenAI Model",
        options=["openai/o3-mini"],
        index=0,
        key="openai_model"
    )
    if st.button("Select OpenAI", key="select_openai"):
        st.session_state.current_model = openai_model
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    deepseek_selected = st.session_state.current_model.startswith('deepseek')
    deepseek_class = "model-card selected-model" if deepseek_selected else "model-card"
    
    st.markdown(f'<div class="{deepseek_class}">', unsafe_allow_html=True)
    st.image("https://deepseek.com/logo.png", width=100)
    st.markdown("<h4>DeepSeek Models</h4>", unsafe_allow_html=True)
    deepseek_model = st.selectbox(
        "Select DeepSeek Model",
        options=["deepseek/deepseek-reasoner"],
        index=0,
        key="deepseek_model"
    )
    if st.button("Select DeepSeek", key="select_deepseek"):
        st.session_state.current_model = deepseek_model
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    google_selected = st.session_state.current_model.startswith('google')
    google_class = "model-card selected-model" if google_selected else "model-card"
    
    st.markdown(f'<div class="{google_class}">', unsafe_allow_html=True)
    st.image("https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Google_Gemini_AI_logo.max-1000x1000.png", width=100)
    st.markdown("<h4>Google Models</h4>", unsafe_allow_html=True)
    google_model = st.selectbox(
        "Select Google Model",
        options=["google/gemini-2.0-pro-exp-02-05"],
        index=0,
        key="google_model"
    )
    if st.button("Select Google", key="select_google"):
        st.session_state.current_model = google_model
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with st.container():
    anthropic_selected = st.session_state.current_model.startswith('anthropic')
    anthropic_class = "model-card selected-model" if anthropic_selected else "model-card"
    
    st.markdown(f'<div class="{anthropic_class}">', unsafe_allow_html=True)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Anthropic_logo.svg/1200px-Anthropic_logo.svg.png", width=100)
    st.markdown("<h4>Anthropic Models</h4>", unsafe_allow_html=True)
    anthropic_model = st.selectbox(
        "Select Anthropic Model",
        options=["anthropic/sonnet3.7"],
        index=0,
        key="anthropic_model"
    )
    if st.button("Select Anthropic", key="select_anthropic"):
        st.session_state.current_model = anthropic_model
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Display current model
st.markdown(f"<h3>Currently using: {st.session_state.current_model}</h3>", unsafe_allow_html=True)

# Chat interface
st.markdown("<h3>Chat with AI</h3>", unsafe_allow_html=True)

# Display chat history
display_chat_history()

# Input for new message
user_input = st.text_area("Type your message here:", key="user_input", height=100)

# Buttons for actions
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("Send", key="send_button"):
        if user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({
                "content": user_input,
                "is_user": True
            })
            
            # Generate response
            with st.spinner("AI is thinking..."):
                response = generate_response(
                    user_input,
                    st.session_state.current_model,
                    st.session_state.temperature,
                    st.session_state.max_tokens
                )
            
            # Add AI response to chat history
            st.session_state.chat_history.append({
                "content": response,
                "is_user": False
            })
            
            # Clear input
            st.session_state.user_input = ""
            
            # Rerun to update UI
            st.experimental_rerun()

with col2:
    if st.button("Clear Chat", key="clear_button"):
        st.session_state.chat_history = []
        st.experimental_rerun()

with col3:
    if st.button("Save Chat", key="save_button"):
        # Generate a timestamp for the filename
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"chat_history_{timestamp}.json"
        
        # Convert chat history to JSON
        chat_json = json.dumps(st.session_state.chat_history, indent=2)
        
        # Create a download button
        st.download_button(
            label="Download Chat History",
            data=chat_json,
            file_name=filename,
            mime="application/json"
        )

# Feature tabs
st.markdown("---")
st.markdown("<h3>Additional Features</h3>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📝 Text Generation", "🖼️ Image Generation", "📊 Data Analysis"])

with tab1:
    st.markdown("<h4>Text Generation</h4>", unsafe_allow_html=True)
    
    text_prompt = st.text_area(
        "Enter a prompt for text generation:",
        placeholder="Write a short story about a robot learning to paint...",
        key="text_prompt",
        height=100
    )
    
    if st.button("Generate Text", key="generate_text_button"):
        if text_prompt:
            with st.spinner("Generating text..."):
                response = generate_response(
                    text_prompt,
                    st.session_state.current_model,
                    st.session_state.temperature,
                    st.session_state.max_tokens
                )
            
            st.markdown("<div class='stCard'>", unsafe_allow_html=True)
            st.markdown("<h5>Generated Text:</h5>", unsafe_allow_html=True)
            st.markdown(response)
            st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<h4>Image Generation</h4>", unsafe_allow_html=True)
    st.markdown("Note: Currently only available with OpenAI API key")
    
    image_prompt = st.text_area(
        "Enter a prompt for image generation:",
        placeholder="A futuristic city with flying cars and neon lights...",
        key="image_prompt",
        height=100
    )
    
    image_size = st.selectbox(
        "Select image size:",
        options=["1024x1024", "512x512", "256x256"],
        index=0,
        key="image_size"
    )
    
    if st.button("Generate Image", key="generate_image_button"):
        if image_prompt:
            if not st.session_state.api_keys['openai']:
                st.error("OpenAI API key is required for image generation")
        else:
                with st.spinner("Generating image..."):
                    try:
                        client = OpenAI(api_key=st.session_state.api_keys['openai'])
                        response = client.images.generate(
                            model="dall-e-3",
                            prompt=image_prompt,
                            size=image_size,
                            quality="standard",
                            n=1,
                        )
                        
                        image_url = response.data[0].url
                        
                        # Display the generated image
                        st.markdown("<div class='stCard'>", unsafe_allow_html=True)
                        st.markdown("<h5>Generated Image:</h5>", unsafe_allow_html=True)
                        st.image(image_url, caption=image_prompt, use_column_width=True, output_format="JPEG", clamp=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Error generating image: {str(e)}")

with tab3:
    st.markdown("<h4>Data Analysis</h4>", unsafe_allow_html=True)
    
    st.markdown("""
    Upload a CSV file and ask questions about your data.
    The AI will help analyze and interpret your data.
    """)
    
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        import pandas as pd
        
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Display the dataframe
        st.markdown("<h5>Data Preview:</h5>", unsafe_allow_html=True)
        st.dataframe(df.head())
        
        # Data analysis prompt
        data_question = st.text_area(
            "Ask a question about your data:",
            placeholder="What are the key insights from this data?",
            key="data_question",
            height=100
        )
        
        if st.button("Analyze Data", key="analyze_data_button"):
            if data_question:
                # Create a prompt that includes the data information
                data_info = f"DataFrame info:\n{df.info()}\n\nDataFrame description:\n{df.describe()}\n\nFirst 5 rows:\n{df.head().to_string()}"
                prompt = f"I have the following data:\n\n{data_info}\n\nQuestion: {data_question}\n\nPlease analyze this data and answer my question."
                
                with st.spinner("Analyzing data..."):
                    response = generate_response(
                        prompt,
                        st.session_state.current_model,
                        st.session_state.temperature,
                        st.session_state.max_tokens
                    )
                
                st.markdown("<div class='stCard'>", unsafe_allow_html=True)
                st.markdown("<h5>Analysis Result:</h5>", unsafe_allow_html=True)
                st.markdown(response)
                st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div class="footer">
        <p>This application allows you to interact with various AI models using your own API keys.</p>
        <p>No data is stored on our servers - your API keys and conversations remain private.</p>
        <p>For support or feedback, please contact us at support@aiplayground.example.com</p>
    </div>
    """,
    unsafe_allow_html=True
)


