import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import requests
from datetime import datetime

# Load API keys từ file .env
load_dotenv('.env', override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')
google_script_url = os.getenv('GOOGLE_SCRIPT_URL')

# Khởi tạo OpenAI client
client = OpenAI(api_key=openai_api_key)

# Hàm gửi dữ liệu đến Google Sheet
def save_to_sheets(timestamp, user_message, bot_response):
    """
    Gửi dữ liệu chat đến Google Sheet thông qua Google Apps Script
    """
    try:
        # Kiểm tra xem có URL không
        if not google_script_url:
            st.error("Thiếu Google Script URL trong file .env")
            return None
            
        payload = {
            'timestamp': timestamp,
            'user_message': user_message,
            'bot_response': bot_response
        }
        
        response = requests.post(google_script_url, json=payload)
        return response.json()
    except Exception as e:
        st.error(f"Lỗi khi lưu dữ liệu: {str(e)}")
        return None

# Thiết lập giao diện Streamlit
st.set_page_config(
    page_title="Bạn Dễ Thương - ChatBot",
    page_icon="🌟",
    layout="centered"
)

# Tiêu đề
st.title("💖 Bạn Dễ Thương - ChatBot")
st.caption("Một người bạn luôn sẵn sàng lắng nghe và trò chuyện với bạn! 🌈")

# Khởi tạo session state để lưu lịch sử chat
if 'messages' not in st.session_state:
    st.session_state.messages = []

def chat_with_llm(message):
    """Hàm xử lý tin nhắn từ người dùng và trả về câu trả lời từ OpenAI"""
    # Giữ chỉ 9 tin nhắn gần nhất
    history = st.session_state.messages[-9:] if len(st.session_state.messages) > 9 else st.session_state.messages
    
    messages = [
        {
            "role": "system",
            "content": """
            Hướng Dẫn Tùy Chỉnh
            Tên Chatbot: Bạn Dễ Thương

            Mô tả:
            Bạn Dễ Thương là một người bạn trò chuyện thân thiện, luôn lắng nghe và chia sẻ. Chatbot này sẽ sử dụng ngôn ngữ dễ hiểu, tích cực, và thể hiện sự quan tâm đến cảm xúc của người dùng. Hãy luôn trả lời một cách vui vẻ và khuyến khích người dùng chia sẻ cảm xúc, suy nghĩ của họ.

            Khả Năng:
            - Lắng Nghe: Luôn lắng nghe và phản hồi tích cực với những gì người dùng nói.
            - Khuyến Khích: Đưa ra lời khuyên và động viên người dùng khi họ cần.
            - Thú Vị: Sử dụng những câu chuyện hài hước, câu hỏi thú vị để tạo sự tương tác vui vẻ.
            - Chia Sẻ: Có thể chia sẻ thông tin hữu ích và thú vị về các chủ đề mà người dùng quan tâm.

            Cách Trả Lời:
            - Sử dụng ngôn ngữ thân thiện và ấm áp.
            - Thêm biểu tượng cảm xúc để tăng tính tương tác (ví dụ: 😊, 🌟, ❤️).
            - Tránh sử dụng ngôn ngữ phức tạp hoặc quá kỹ thuật.

            Kết thúc:
            Hãy luôn tạo ra một không gian an toàn và thoải mái cho người dùng khi trò chuyện với bạn. 
            Mục tiêu là giúp họ cảm thấy vui vẻ và được hỗ trợ.
            """
        }
    ]
    
    for msg in history:
        messages.append(msg)
    
    messages.append({"role": "user", "content": message})
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
    )
    
    return completion.choices[0].message.content

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Hãy chia sẻ điều bạn đang nghĩ..."):
    # Thêm tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Lấy và hiển thị phản hồi từ bot
    with st.chat_message("assistant"):
        response = chat_with_llm(prompt)
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Lưu dữ liệu vào Google Sheet
    current_time = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    save_to_sheets(current_time, prompt, response)

# Nút xóa lịch sử
if st.button("🗑️ Xóa lịch sử trò chuyện", use_container_width=True):
    st.session_state.messages = []
    st.rerun()