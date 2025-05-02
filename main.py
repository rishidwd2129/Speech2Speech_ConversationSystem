from fastapi import FastAPI, Query
import ollama
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import io
import soundfile as sf
import numpy as np
from typing import Optional
from Pipeline.Text2Speech.Text2Speech import textToSpeech
from Pipeline.Stream.SpeechStream import stream
app = FastAPI()
tts_engine = textToSpeech()
# @app.get("/Generate")  # Changed to GET since we're using query params
def generate(prompt: str = Query(..., description="The input prompt for the model")):
    """
    Generate a response from the model based on the provided prompt.
    """
    response = ollama.chat(model="deepseek-r1:7b", messages=[{"role": "user", "content": prompt}])
    return {"response": response["message"]["content"]}  # Fixed typo: "messages" → "message"



  # Initialize once (loads models)

@app.get("/speak")
async def text2speech(text: str):
    result = generate(text)
    output_text = result["response"]
    
    stream(tts_engine, output_text)
    # max_length = 550  # Keep a little buffer <600
    # if len(output_text) > max_length:
    #     output_text = output_text[:max_length]
    
    # tts_engine.speak(output_text)

    return {"status": "success", "message": "Audio played successfully"}



