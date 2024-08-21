
Run API: python -m uvicorn yt_chat_api:app
Run Interface: streamlit run yyy_interface.py
####
1. Ask Question Endpoint

URL: /ask/

Method: GET

Description: ask questions related to videos (including asking for a summary) + provide youtube video link (or multiple) 

Request Parameters: "query" : Query string to ask

