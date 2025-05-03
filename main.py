import threading
from fastapi import FastAPI, Query
import ollama
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import io
import soundfile as sf
import numpy as np
from typing import Optional
from Pipeline.Text2Speech.Text2Speech import textToSpeech
from Pipeline.Stream.SpeechStream import SharedState
app = FastAPI()
tts_engine = textToSpeech()  # Initialize once (loads models) 
shared_state = SharedState(tts_engine ,max_buffer_size=3)
# @app.get("/Generate")  # Changed to GET since we're using query params
def generate(prompt: str = Query(..., description="The input prompt for the model")):
    """
    Generate a response from the model based on the provided prompt.
    """
    response = ollama.chat(model="deepseek-r1:7b", messages=[{"role": "user", "content": prompt}])
    return {"response": response["message"]["content"]} 



  # Initialize once (loads models)

@app.get("/speak")
async def text2speech(text: str):
    result = generate(text)
    output_text = result["response"]
    
    producer = threading.Thread(target=shared_state.producer_function, args=(output_text,),daemon=True)
    consumer = threading.Thread(target=shared_state.stream, daemon=True)
    
    producer.start()
    consumer.start()

    producer.join()
    consumer.join()

    return {"status": "success", "message": "Audio played successfully"}



