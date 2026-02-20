from gtts import gTTS
import os

mytext = "Hello world"

# Pass text to the engine
myobj = gTTS(text=mytext, lang='en', slow=False)

# Save converted audio in mp3 file
myobj.save("welcome.mp3")

# Play converted file
os.system("start welcome.mp3")