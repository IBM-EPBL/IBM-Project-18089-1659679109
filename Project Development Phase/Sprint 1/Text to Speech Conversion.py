import pyttsx3

def TexttoSpeech(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()
    
text=input("Enter the text ")
TexttoSpeech(text)