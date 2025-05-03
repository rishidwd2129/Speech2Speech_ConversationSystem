import threading
import re

class SharedState:
    def __init__(self, tts_engine, max_buffer_size=5):
        self.buffer = []
        self.lock = threading.Lock()
        self.condition = threading.Condition()
        self.production_complete = False
        self.max_buffer_size = max_buffer_size
        self.tts_engine = tts_engine

    def producer_function(self, text: str):
        """Instance method that produces audio chunks"""
        think_tag_regex = r'<think>.*?</think>'
        text = re.sub(think_tag_regex, '', text, flags=re.DOTALL)
        
        for textset in text.split("\n"):
            if len(textset) > 0:
                audio = self.tts_engine.synthesize(textset)  # Use textset instead of text
                with self.condition:
                    while len(self.buffer) >= self.max_buffer_size:
                        self.condition.wait()
                    
                    self.buffer.append(audio)
                    print(f"Appended audio chunk to buffer (size: {len(self.buffer)})")
                    self.condition.notify()
        
        with self.condition:
            self.production_complete = True
            self.condition.notify_all()

    def stream(self):
        """Instance method that consumes audio chunks"""
        while True:
            with self.condition:
                while not self.buffer and not self.production_complete:
                    self.condition.wait()
                
                if not self.buffer and self.production_complete:
                    break
                
                data = self.buffer.pop(0)
                self.condition.notify()
                print(f"Playing audio chunk (remaining: {len(self.buffer)})")
            
            self.tts_engine.speak(data)