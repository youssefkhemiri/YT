import streamlit as st
from openai import OpenAI

# Set your OpenAI API key
client = OpenAI()

# Streamlit app
st.title("Youtube Agent 🤖")

# Sidebar for settings
st.sidebar.title("Settings")
# temperature = st.sidebar.text_input("Youtube URL")
max_tokens = st.sidebar.text_input("OpenAI KEY")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
##

import requests

def youtube_agent_api(query, url = "http://54.144.77.43/ask/"):

    url = "http://localhost:8000/ask/"

    data = {"query": query}

    response = requests.post(url, json=data)

    return response

# Input box for the user's message
if user_input := st.chat_input("You:"):
    # Add user's message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)
    
    print("###############")
    print(st.session_state.messages)
    print("###############")
    response = youtube_agent_api(user_input)
    
    # Get the assistant's response
    assistant_message = response.json()["answer"]
    
    # Add assistant's response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_message})
    
    # Display assistant's response
    with st.chat_message("assistant"):
        st.markdown(assistant_message)

    st.rerun()
