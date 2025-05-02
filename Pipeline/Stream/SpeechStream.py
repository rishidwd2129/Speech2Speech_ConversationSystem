from ..Text2Speech.Text2Speech import textToSpeech
import re
def stream(tts_engine,text : str):
    """
    Input large chunks of strigs and stream it to TTS engine
    """
    think_tag_regex = r'<think>.*?</think>'
    text = re.sub(think_tag_regex, '', text, flags=re.DOTALL)


    for textset in text.split("\n"):
        if len(textset) > 0:
            tts_engine.speak(textset)
        
            
    