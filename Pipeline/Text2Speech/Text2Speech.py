import torch
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import sounddevice as sd
import numpy


class textToSpeech:

    def __init__(self):

        # Hardware acceleration
        # if torch.cuda.is_available():
        #     self.device = torch.device("cuda")
        # elif torch.backends.mps.is_available():
        #     self.device = torch.device("mps")
        # else:
        #     self.device = torch.device("cpu")
        self.device = torch.device("cpu")
        print(f"Using device: {self.device}")

        self.processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        self.model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
        self.model.to(self.device)
        self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
        self.vocoder.to(self.device)
        # Get speaker embedding
        embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        self.speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
        self.speaker_embeddings = self.speaker_embeddings.to(self.device)
        
    
    def synthesize(self, text):
        inputs = self.processor(text=text, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
           speech = self.model.generate_speech(inputs["input_ids"], self.speaker_embeddings, vocoder=self.vocoder)
           if speech.device.type != "cpu" :
                print("Moving speech to CPU")
                speech = speech.cpu()
        return speech.numpy()
    
    async def speak(self, text):
        audio = self.synthesize(text)
        sd.play(audio, samplerate=16000)
        sd.wait()  # Wait until audio is finished playing
        return 


if __name__ == "__main__":
    tts = textToSpeech()  # Initialize once (loads models)
    tts.speak("Hello world! This is a test of text to speech.")