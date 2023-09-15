# Third-party imports
import openai
import streamlit as st
import requests
from dotenv import load_dotenv
import os
import time
from fastapi import FastAPI, Form, Depends
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Internal imports
from models import Conversation, SessionLocal
from utils import send_message, logger


app = FastAPI()
# Set up the OpenAI API client
openai.api_key = config("OPENAI_API_KEY")
whatsapp_number = config("TO_NUMBER")

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

#d-id
def generate_video(prompt, avatar_url, gender):
    url = "https://api.d-id.com/talks"
    headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Basic ZDJsdVpHUnlZVzVuWlhKcWFHOXlaR0Z1UUdkdFlXbHNMbU52YlE6VmF4bHNGWG5Qa1UtSnZ0VVU0eVgzOmQybHVaR1J5WVc1blpYSnFhRzl5WkdGdVFHZHRZV2xzTG1OdmJROlZheGxzRlhuUGtVLUp2dFVVNHlYMw=="
}
    if gender == "Female":
        payload = {
            "script": {
                "type": "text",
                "subtitles": "false",
                "provider": {
                    "type": "microsoft",
                    "voice_id": "en-US-ChristopherNeural"
                },
                "ssml": "false",
                "input":prompt
            },
            "config": {
                "fluent": "false",
                "pad_audio": "0.0"
            },
            "source_url": "https://clips-presenters.d-id.com/matt/9C51DD6lgH/mBHOFBuOHq/image.png"
        }

    if gender == "Male":
        payload = {
            "script": {
                "type": "text",
                "subtitles": "false",
                "provider": {
                    "type": "microsoft",
                    "voice_id": "en-US-ChristopherNeural"
                },
                "ssml": "false",
                "input":prompt
            },
            "config": {
                "fluent": "false",
                "pad_audio": "0.0"
            },
            "source_url": "https://clips-presenters.d-id.com/matt/9C51DD6lgH/mBHOFBuOHq/image.png"
        }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print(response.text)
            res = response.json()
            id = res["id"]
            status = "created"
            while status == "created":
                getresponse =  requests.get(f"{url}/{id}", headers=headers)
                print(getresponse)
                if getresponse.status_code == 200:
                    status = res["status"]
                    res = getresponse.json()
                    print(res)
                    if res["status"] == "done":
                        video_url =  res["result_url"]
                    else:
                        time.sleep(10)
                else:
                    status = "error"
                    video_url = "error"
        else:
            video_url = "error"   
    except Exception as e:
        print(e)      
        video_url = e      
        
    return video_url

@app.post("/message")
async def reply(Body: str = Form(), db: Session = Depends(get_db)):
    # Call the OpenAI API to generate text with GPT-3.5
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=Body,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5,
    )

    # The generated text
    chat_response = response.choices[0].text.strip()
    avatar_url="https://www.thesun.co.uk/wp-content/uploads/2021/10/2394f46a-c64f-4019-80bd-445dacda2880.jpg?w=670"
    avatar_selection="Male"
    videourl=generate_video(chat_response, avatar_url, avatar_selection)
    print(videourl)

    try:
            videourl=generate_video(chat_response, avatar_url, avatar_selection)  # Call your video generation function here
            if videourl!= "error":
               videourl=videourl
            else:
                videourl=("Sorry... Try again")
    except Exception as e:
            print(e)
            videourl=generate_video(chat_response, avatar_url, avatar_selection)



    # Store the conversation in the database
    # try:
    #     conversation = Conversation(
    #         sender=whatsapp_number,
    #         message=Body,
    #         response=videourl
    #         )
    #     db.add(conversation)
    #     db.commit()
    #     logger.info(f"Conversation #{conversation.id} stored in database")
    # except SQLAlchemyError as e:
    #     db.rollback()
    #     logger.error(f"Error storing conversation in database: {e}")
    print(f"print {videourl}")
    send_message(whatsapp_number, videourl)
    return ""
