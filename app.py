import os
import re
import streamlit as st
import json
from utils.css_loader import load_css
from utils.session_utils import toggle_pdf_chat, track_index, clear_cache, get_timestamp
from utils.vectorstore_utils import setup_vectorstore, create_chain
from utils.document_loader import load_document
from utils.history_manager import  load_chat_history_json, save_chat_history
from groq import Groq

with open("config.json", "r") as f:
    config = json.load(f)

def main():
    load_css("styles/style.css")
    working_dir = os.path.dirname(os.path.abspath(__file__))

    st.title("MULTIMODAL LOCAL CHAT APP")
    if 'go_to_chat' not in st.session_state:
        st.session_state['go_to_chat'] = False

    if not st.session_state['go_to_chat']:
        st.markdown("""
            <div class="intro" style="text-align: center;">
                <h3>Welcome to the Multimodal Local Chat App!</h3>
                <p>Our application allows you to upload PDF documents and chat with an intelligent assistant.</p>
            </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1.5])  
        with col2:  
            if st.button("Go to Chat", key="go_to_chat_button", help="Click to go to chat page", on_click=lambda: st.session_state.update(go_to_chat=True)):
                st.session_state['go_to_chat'] = True  

    else:
        st.sidebar.title("Chat Session")
        if st.sidebar.button("Home", on_click=lambda: st.session_state.update(go_to_chat=False)):
            st.session_state['go_to_chat'] = False

        chat_container = st.container()
        chat_sessions = ["Chat_New"] + os.listdir(config["CHAT_HISTORY_PATH"])

        if "send_input" not in st.session_state:
            st.session_state.session_key = "Chat_New"
            st.session_state.new_session_key = None
            st.session_state.session_index_tracker = "Chat_New"
            st.session_state.audio_uploader_key = 0
            st.session_state.pdf_uploader_key = 1
            st.session_state.model_tracker = None
            st.session_state.send_input = False
            st.session_state.pdf_chat = False
            st.session_state.history = []
            st.session_state.conversation_chain = None

        index = chat_sessions.index(st.session_state.session_index_tracker) if st.session_state.session_index_tracker in chat_sessions else 0
        st.sidebar.selectbox("Select a chat session", chat_sessions, key="session_key", index=index, on_change=track_index)

        if "history" not in st.session_state:
            st.session_state.history = []
            
        for message in st.session_state.history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        #Load history chat
        if st.session_state.session_key != "Chat_New":
            st.session_state.history = load_chat_history_json(os.path.join(config["CHAT_HISTORY_PATH"], st.session_state.session_key))
        else:
            st.session_state.history = []  

        if st.session_state.session_key == "Chat_New" and st.session_state.new_session_key is not None:
            st.session_state.session_index_tracker = st.session_state.new_session_key
            st.session_state.new_session_key = None

        pdf_toggle_col = st.sidebar.columns(2)[0] 
        pdf_toggle_col.toggle("PDF Chat", key="pdf_chat", value=False, on_change=clear_cache)

        chat_container = st.container()
        user_input = st.chat_input("Type your message here", key="user_input")

        uploaded_pdf = st.sidebar.file_uploader(
            "Chọn file PDF để tải lên", 
            accept_multiple_files=True,
            key=st.session_state.pdf_uploader_key,
            type=["pdf"],
            on_change=toggle_pdf_chat,
            label_visibility="collapsed" 
        )

        if uploaded_pdf:
            with st.spinner("Processing PDF..."):
                file_path = os.path.join(working_dir, uploaded_pdf[0].name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_pdf[0].getbuffer())  
                if "vectorstore" not in st.session_state:
                    st.session_state.vectorstore = setup_vectorstore(load_document(file_path))
                if st.session_state.conversation_chain is None:
                    st.session_state.conversation_chain = create_chain(st.session_state.vectorstore, temperature=0.5, groq_api_key=config["GROQ_API_KEY"])

        if user_input:
            if st.session_state.pdf_chat and uploaded_pdf:
                vectorstore = setup_vectorstore(load_document(file_path))  
                chain = create_chain(vectorstore, temperature=0.5,groq_api_key=config["GROQ_API_KEY"])
                response = chain({"question": user_input})
                assistant_response = response["answer"]
                
                st.session_state.history.append({"role": "user", "content": user_input})
                st.session_state.history.append({"role": "assistant", "content": assistant_response})
                
            else:    
                st.session_state.history.append({"role": "user", "content": user_input})
        
                GROQ_API_KEY = config["GROQ_API_KEY"]
                os.environ["GROQ_API_KEY"] = GROQ_API_KEY
                client = Groq()
                
                messages = [
                    {"role": "system", "content": "You are a helpful assistant"},
                    *st.session_state.history
                ]
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages
                )
            
                assistant_response = response.choices[0].message.content
                st.session_state.history.append({"role": "assistant", "content": assistant_response})
            
            if st.session_state.session_key == "Chat_New":
                sanitized_session_key = re.sub(r'[,:]', '-', get_timestamp())
                st.session_state.new_session_key = sanitized_session_key  
               
            else:
                st.session_state.new_session_key = None  
                
            # Save chat
            save_chat_history(
                st.session_state.history, 
                config, 
                st.session_state.session_key,  
                st.session_state.new_session_key
            )

        if st.session_state.history:
            with chat_container:
                for message in st.session_state.history:
                    st.chat_message(message["role"]).write(message["content"])

if __name__ == "__main__":
    main()
