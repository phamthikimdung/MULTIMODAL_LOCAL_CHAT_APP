import re
from datetime import datetime
import streamlit as st

def toggle_pdf_chat():
    st.session_state.pdf_chat = True
    clear_cache()

def detoggle_pdf_chat():
    st.session_state.pdf_chat = False

def track_index():
    st.session_state.session_index_tracker = st.session_state.session_key

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_session_key():
    if st.session_state.session_key == "Chat_New":
        st.session_state.new_session_key = sanitize_timestamp(get_timestamp())
        return st.session_state.new_session_key
    return st.session_state.session_key

def sanitize_timestamp(timestamp):
    return re.sub(r'[,:]', '-', timestamp)

def clear_cache():
    st.cache_resource.clear()
