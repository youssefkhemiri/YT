########################################
##############Version4################
########################################
from unittest import result
from fastapi import FastAPI, Query
from typing import Dict
import os
import shutil
from langchain_community.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain.chains import AnalyzeDocumentChain
import json
from openai import OpenAI as OpenAI
from youtube_transcript_api import YouTubeTranscriptApi as yta
from youtube_transcript_api.formatters import JSONFormatter
from googleapiclient.discovery import build
from isodate import parse_duration

# ###Greaserails###
from grease_rails import GreaseRails
def initialize_grease_rails():
    # initialize GreaseRails object
    grease_rails_object = GreaseRails()
    return grease_rails_object

grease_rails = initialize_grease_rails()    
grease_rails.load_script_txt_to_class()

def maingreaserails(user_query = "How to use this youtube bot?", redirect = None):
    # grease_rails = initialize_grease_rails()    
    # grease_rails.load_script_txt_to_class()

    print(f"user_query: {user_query}")
    grease_rails_response = grease_rails.return_grease_rails_agent_response(user_query)
    if grease_rails_response == "GreaseRails miss":
        print("Redirect this answer...")
        return "No"
    else: 
        print("Riding the GreaseRails")
        agent_response = grease_rails_response
        print(f"agent_response: {agent_response}")
    print("------------- xxxxxxxxxxx ----------------")
    print(f"user_query: {user_query}")
    
    print("done GR")
    return agent_response

###OpenAI Function calling###    
def analyze_fn_calling(question):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "question_about_video",
                "description": "a question about the given youtube video",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "video_ids": {
                            "type": "string",
                            "description": """a list containing the given youtube video ids for example for https://www.youtube.com/watch?v=ABC123 and https://www.youtube.com/watch?v=EFJ123 the extracted id list is ["ABC123", "EFJ123"], if the youtube url is https://www.youtube.com/watch?v=ABC123&list=PL123456 the extracted id list is ["ABC123"] only because the url is in long format"""
                        },
                        "question": {
                            "type": "string",
                            "description": "extract the user's question about the YouTube video. example: what is the relativity theory, https://www.youtube.com/watch?v=ABC123 . the output is 'what is the relativity theory?', the question can be found before or after the video url"
                        }
                    },
                    "required": ["video_ids", "question"]
                },
            },
        },

        {
            "type": "function",
            "function": {
                "name": "notes_with_timestamps",
                "description": "use this if the user asks for the video notes, bullets points, key notes, or key points",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "video_ids": {
                            "type": "string",
                            "description": """a list containing the given youtube video ids for example for https://www.youtube.com/watch?v=ABC123 and https://www.youtube.com/watch?v=EFJ123 the extracted id list is ["ABC123", "EFJ123"], if the youtube url is https://www.youtube.com/watch?v=ABC123&list=PL123456 the extracted id list is ["ABC123"] only because the url is in long format"""
                        },
                        "question": {
                            "type": "string",
                            "description": "extract the user's question about the YouTube video. example: what is the relativity theory, https://www.youtube.com/watch?v=ABC123 . the output is 'what is the relativity theory?'"
                        }
                    },
                    "required": ["video_ids", "question"]
                },
            },
        },


        {
            "type": "function",
            "function": {
                "name": "summarize_video",
                "description": "use this function if the user specifically asks for a summary",
                "parameters": {
                    "type": "object",
                        "properties": {
                            "video_ids": {
                            "type": "string",
                            "description": """a list containing the given youtube video ids for example for https://www.youtube.com/watch?v=ABC123 and https://www.youtube.com/watch?v=EFJ123 the extracted id list is ["ABC123", "EFJ123"], if the youtube url is https://www.youtube.com/watch?v=ABC123&list=PL123456 the extracted id list is ["ABC123"] only because the url is in long format"""
                            },
                        "question": {
                            "type": "string",
                            "description": "extract and better formulate the user's inquiry about the YouTube video"
                        }
                        
                    },
                    "required": ["video_ids", "question"]
                },
            },
        },

    ]



    client = OpenAI()


    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": question}],
        tools=tools, # type: ignore
        tool_choice="auto",  # auto is default, but we'll be explicit
    )

    return (response.choices[0].message)

###Video ids extracted from the FC message + fixes###
def extract_video_ids(completion_message, function_name):
    print(function_name)
    video_ids = []
    question = ""
    for tool_call in completion_message.tool_calls:
        if tool_call.function.name == function_name:
            arguments = tool_call.function.arguments
            arguments = json.loads(arguments)
            if 'video_ids' in arguments:
                video_ids.extend(arguments['video_ids'])
                question = arguments.get('question', None)
                print("--------", question)
    return fix_id(video_ids), question

# def fix_id(video_ids):
#     if len(video_ids) != 0:
#         if len(video_ids[0]) == 1:
#             i = ''.join(video_ids)
#             print("------------------>",i,"<------------------")
#             return [i]
#     return video_ids

def fix_id(input_list):
    result = []
    temp_str = ""
    for char in input_list:
        if char == ',':
            if temp_str:
                result.append(temp_str)
                temp_str = ""
        elif char != ' ':
            temp_str += char
    # Add the last group if not empty
    if temp_str:
        result.append(temp_str)
    print("------------------>",result,"<------------------")
    return result

###Summarize Video with Langchain###
def summarize_video(video_id):
    loader = YoutubeLoader(video_id)
    docs = loader.load()  
    if len(docs) == 0:
        return f"No video found for {video_id}"
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=7000, chunk_overlap=200)
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106") #gpt-3.5-turbo-1106
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    summarize_document_chain = AnalyzeDocumentChain(
        combine_docs_chain=chain, text_splitter=text_splitter
    )
    result = summarize_document_chain.run(docs[0].page_content)
    return result

###QA###
def create_batches(video_id, max_words_per_batch = 1000):
    
    try:
        transcript = yta.get_transcript(video_id)
    except Exception as e:
        print(f"Error during getting transcript: {e}")
        return "Can't find the video"

    formatter = JSONFormatter()
    json_formatted = formatter.format_transcript(transcript, indent=2)

    batches = []
    current_batch = {"text": [], "start": None, "end": None}
    current_word_count = 0

    for item in transcript:
        text = item["text"]
        words = text.split()
        duration = item["duration"]

        # Check if adding this item exceeds max_words_per_batch
        if current_word_count + len(words) > max_words_per_batch:
            # Add current batch to batches
            if current_batch["text"]:
                batches.append({
                    "text": " ".join(current_batch["text"]),
                    "start": calculate_time(current_batch["start"]),
                    "end": calculate_time(current_batch["end"])
                })
            # Reset current batch
            current_batch = {"text": [], "start": None, "end": None}
            current_word_count = 0

        # Add item to current batch
        current_batch["text"].append(text)
        if current_batch["start"] is None:
            current_batch["start"] = item["start"]
        current_batch["end"] = item["start"] + duration
        current_word_count += len(words)


    # Add the last batch
    if current_batch["text"]:
        batches.append({
            "text": " ".join(current_batch["text"]),
            "start": calculate_time(current_batch["start"]),
            "end": calculate_time(current_batch["end"])
        })

    return batches

client = OpenAI()

def recursive_answering(batches, questionn, i=0, answer=""):
    if i >= len(batches):
        return answer.strip()  # Remove leading/trailing whitespaces
    
    # Update the prompt to be more directive and structured
    prompttt = (f"Given the question and context below, please refine the previous answer or provide a new one based on the context provided and previous answer. Only answer relying on the context and previous answer\n\n"
              f"Question: {questionn}\n\n"
              f"Context: {batches[i]['text']}\n\n"
              f"Previous Answer: {answer}\n\n"
              f"Refined Answer:")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompttt}],
            temperature=0
        )
        new_answer = response.choices[0].message.content  # Cleanup response
    except Exception as e:
        print(f"Error during API call: {e}")
        return answer  # Return the last successful answer in case of an error

    print(f"----Response{i+1}-----")
    print(questionn)
    print(new_answer)
    # Proceed to the next iteration with the updated answer
    return recursive_answering(batches, questionn, i + 1, str(new_answer))

###Notes with Timestamps###
def calculate_time(t):
    # calculate the accurate time according to the given duration
    hours = int(t // 3600)
    min = int((t // 60) % 60)
    sec = int(t % 60)
    return f"{hours}:{min}:{sec}"

def notes_with_timestamps(video_id, question, max_words_per_batch = 3000):
    try:
        transcript = yta.get_transcript(video_id)
    except Exception as e:
        print(f"Error during getting transcript: {e}")
        return "Can't find the video"
    
    formatter = JSONFormatter()
    json_formatted = formatter.format_transcript(transcript, indent=2)

    batches = []
    current_batch = {"text": [], "start": None, "end": None}
    current_word_count = 0

    for item in transcript:
        text = item["text"]
        words = text.split()
        duration = item["duration"]

        # Check if adding this item exceeds max_words_per_batch
        if current_word_count + len(words) > max_words_per_batch:
            # Add current batch to batches
            if current_batch["text"]:
                batches.append({
                    "text": " ".join(current_batch["text"]),
                    "start": calculate_time(current_batch["start"]),
                    "end": calculate_time(current_batch["end"])
                })
            # Reset current batch
            current_batch = {"text": [], "start": None, "end": None}
            current_word_count = 0

        # Add item to current batch
        current_batch["text"].append(text)
        if current_batch["start"] is None:
            current_batch["start"] = item["start"]
        current_batch["end"] = item["start"] + duration
        current_word_count += len(words)


    # Add the last batch
    if current_batch["text"]:
        batches.append({
            "text": " ".join(current_batch["text"]),
            "start": calculate_time(current_batch["start"]),
            "end": calculate_time(current_batch["end"])
        })

    client = OpenAI()


    Summary = ""
    for item in batches:
        print("-")
        prompt = f"""
        You are a given a batch timestamps of a part of a youtube video, return main key points (in form of bullet points) and keep it short. dont mention its a video or anything else, just the key points.:
        {item}
        only return the key points.
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        Summary += f"Time: {item['start']} - {item['end']}\n" + str(response.choices[0].message.content) + "\n\n"
   
    print("--")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[{"role": "user", "content": f"formulate these notes to answer properly this question: {question}, keep bullet points style: {Summary}"}],
        temperature=0
    )

    # print(response.choices[0].message.content)
    return response.choices[0].message.content

import re
def contains_youtube_url(text):
    # Simple regular expression to find 'youtube.com' or 'youtu.be' in a string
    pattern = r"(youtube\.com|youtu\.be)"
    return bool(re.search(pattern, text))

import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
class QueryModel(BaseModel):
    query: str
# from urllib.parse import unquote


def get_video_details(video_id, youtube_api_key= ''):
    # Build the service object for the YouTube API
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    
    # Make a request to get video details
    request = youtube.videos().list(
        part="snippet,contentDetails",
        id=video_id
    )
    response = request.execute()
    
    # Extract video title, description, thumbnail URL, and duration from the response
    if response['items']:
        title = response['items'][0]['snippet']['title']
        description = response['items'][0]['snippet']['description']
        thumbnails = response['items'][0]['snippet']['thumbnails']
        thumbnail_url = thumbnails['high']['url']  # 'high' quality thumbnail

        duration_iso8601 = response['items'][0]['contentDetails']['duration']
        duration = parse_duration(duration_iso8601)  # Converts ISO 8601 duration to a timedelta object
        
        return title, description, thumbnail_url, str(duration)
    else:
        return "No video found with that ID", "", "", ""

###API FastAPI###
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Youtube Agent API"}

@app.post("/ask/")
async def ask_question2(query_body: QueryModel):
    query = query_body.query

    if not query:
        raise HTTPException(status_code=407, detail="No query provided.")
    
    print(">>>>> Query: ", query)

    try:
        # start_time = time.time()
        gr = maingreaserails(query)
        
        if gr == "No":
            pass
        elif gr == "lololo" or gr == "lololo\n\n":
            grr = """
            Here is a list of things I can do (For each of the following provide the question + youtube video url):
                        
            ### ✨ Video Summarization 
            - **Brief**: Get concise, short summaries of a YouTube video. Ideal for quick insights without needing to watch the entire video. 
            - *Note*: The summary is predefined and the user question does not effect it. Whether you ask for a long summary or a short one ect. the output remains the same.
            - You can provide multiple youtube videos.

            ### ✨ Notes Generation
            - **Comprehensive**: Save time by generating detailed notes from a video. These notes offer more in-depth insights than the summary.
            - **Usage**:
                - *General Notes*: Simply request "Give me notes" to receive notes covering the entire video.

            ### ✨ Question Answering
            - **Insightful**: Have specific questions about video content? This feature provides detailed answers based on the video content, effectively watching the video on your behalf.
            - supports 1 video at a time, if multiple provided, only the first one will be used.
            """
            return {"answer": grr, "credits_flag": 0}  
        else:
            return {"answer": gr, "credits_flag": 0}  
        
        # if ("youtube" not in query) or ("youtu" not in query):
        #     print("-error1-")
        #     print(query)
        #     return {"answer": "Please provide a valid youtube link", "credits_flag": 0}
        if not(contains_youtube_url(query)):
            print("-error1-")
            print(query)
            return {"answer": "Please provide a valid youtube link", "credits_flag": 0}
        

        response = analyze_fn_calling(query)
        print(response)
        

        q=""
        que = ""
        q2 = ""
        summarize_video_ids,q = extract_video_ids(response, 'summarize_video')
        chat_with_bot_ids, que = extract_video_ids(response, 'question_about_video')
        notes_with_timestamps_ids, q2 = extract_video_ids(response, 'notes_with_timestamps')

        if q=="" and q2=="" and que=="":
            return {"answer": "Please provide a query... ", "credits_flag": 0}
        
        if len(summarize_video_ids) != 0:
            print("summ", summarize_video_ids)
            result = ""

            for i, video_id in enumerate(summarize_video_ids):
                title, description, thumbnail_url, duration = get_video_details(video_id)
                # result = result + f"\n Summary{i+1}: \n " + summarize_video(video_id)

                result += (
                            f"\n**Summary {i+1}:**\n"
                            f"\n**Title:** {title}\n"
                            f"\n**Description:** {description}\n"
                            f"\n**Thumbnail URL:** [Link]({thumbnail_url})\n"
                            f"\n**Duration:** {duration}\n"
                            f"\n**Video Summary:**\n" + summarize_video(video_id) + "\n"
                        )
            print(result)
            return {"answer": result, "credits_flag": 1}
        
        if len(notes_with_timestamps_ids) != 0:
            print("notes", notes_with_timestamps_ids)
            print("--question:",q2)
            # return {"answer": notes_with_timestamps(notes_with_timestamps_ids[0])}
            return {"answer": "/n Next Video /n".join([notes_with_timestamps(video_id, q2) for video_id in notes_with_timestamps_ids]), "credits_flag": 1} # type: ignore

        
        if len(chat_with_bot_ids) != 0:
            print("chat", chat_with_bot_ids)
            print(que)
            batches = create_batches(chat_with_bot_ids[0], 3000)
            if batches == "Can't find the video":
                return {"answer": f"Can't find the video {chat_with_bot_ids}", "credits_flag": 0}
            
            answer = recursive_answering(batches, que)
            print(f"final answer from {len(batches)}: ", answer)
            
            # end_time = time.time()
            # print(f"Time taken: {end_time - start_time}")
            return {"answer": answer, "credits_flag": 1}
        
        return {"answer": "Can't find the youtube video, please try again... ", "credits_flag": 0}

    except Exception as e:

        print("--error2--")
        print(e)
        return {"answer": "An error occured, please try again... ", "credits_flag": 0}

# @app.get("/clean/")
# def remove_files():
#     shutil.rmtree(f'./datas')
#     return {"message": f"---- Removed all files ----"}

if __name__ == "__main__":
    maingreaserails()   