import json
import os

def load_chat_history_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

def save_chat_history_json(history, file_path):
    with open(file_path, 'w') as f:
        json.dump(history, f)

def save_chat_history(history, config, session_key, new_session_key=None):
    if history:
        if session_key == "Chat_New":
            sanitized_session_key = new_session_key if new_session_key else "Chat_New"
            file_path = os.path.join(config["CHAT_HISTORY_PATH"], sanitized_session_key + ".json")
        else:
            file_path = os.path.join(config["CHAT_HISTORY_PATH"], session_key)
        save_chat_history_json(history, file_path)
