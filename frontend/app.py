import streamlit as st
import requests
import uuid
from dotenv import load_dotenv
import os
load_dotenv()

UPLOAD_API_URL = os.getenv("UPLOAD_API_URL")
GET_TABLES_API_URL = os.getenv("GET_TABLES_API_URL")
CHAT_API_URL = os.getenv("CHAT_API_URL")

def initialize_new_thread():
    return str(uuid.uuid4())

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {} 
if "thread_id" not in st.session_state:
    st.session_state.thread_id = initialize_new_thread()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "fetch_tables" not in st.session_state:
    st.session_state.fetch_tables = True
if "tables" not in st.session_state:
    st.session_state.tables = []
if "last_selected_table" not in st.session_state:
    st.session_state.last_selected_table = None

# Sidebar: Upload new CSV file
uploaded_file = st.sidebar.file_uploader("Upload a new CSV file", type=["csv"])
if uploaded_file:
    with st.sidebar:
        st.write("Uploading...")
    files = {"file": (uploaded_file.name, uploaded_file.read(), "text/csv")}
    response = requests.post(UPLOAD_API_URL, files=files)

    if response.status_code == 200:
        data = response.json()
        st.sidebar.success(f"Table '{data['table_name']}' created successfully!")
        st.session_state.fetch_tables = True
    else:
        st.sidebar.error(response.json().get("detail", "Error uploading CSV."))

# Sidebar: Fetch available tables
if st.session_state.fetch_tables:
    try:
        response = requests.get(GET_TABLES_API_URL)
        if response.status_code == 200:
            st.session_state.tables = response.json().get("tables", [])
            st.session_state.fetch_tables = False
        else:
            st.sidebar.error("Failed to fetch tables.")
    except Exception as e:
        st.sidebar.error(f"Error fetching tables: {e}")

# Sidebar: Table selection
available_tables = st.session_state.tables
selected_table = st.sidebar.selectbox("Select a table from the database", ["None"] + available_tables)

# Sidebar: Start new chat button
if st.sidebar.button("Start New Chat"):
    st.session_state.thread_id = initialize_new_thread()
    st.session_state.chat_history = []
    st.sidebar.success("Started a new chat session!")

if selected_table != st.session_state.last_selected_table:
    st.session_state.last_selected_table = selected_table
    if selected_table != "None":
        st.session_state.thread_id = initialize_new_thread()
        st.session_state.chat_history = []
        st.sidebar.success(f"Using table: {selected_table}")

st.title("Chat with Your CSV")
st.info(f"Current CHAT ID: {st.session_state.thread_id}")
st.info(f"Using Table: {selected_table}")

# Chat interface
if st.session_state.chat_history:
    for entry in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(entry["message"])
        with st.chat_message("assistant"):
            st.markdown(entry["reply"])

if st.session_state.last_selected_table:
    user_msg = st.chat_input("Enter your query: ")
    if user_msg:

        with st.chat_message("user"):
            st.markdown(user_msg)

        payload = {
            "message": user_msg,
            "table_name": st.session_state.last_selected_table,
            "thread_id": st.session_state.thread_id,
        }
        chat_response = requests.post(CHAT_API_URL, json=payload)

        if chat_response.status_code == 200:

            chat_data = chat_response.json()
            with st.chat_message("assistant"):
                st.markdown(chat_data["reply"])

            st.session_state.chat_history.append(
                {
                    "message": user_msg,
                    "reply": chat_data["reply"],
                }
            )
        else:
            st.error("An error occurred while processing your query. Please try again after some time")

else:
    st.write("Please select a table to start the chat.")