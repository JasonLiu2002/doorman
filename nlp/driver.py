import speech_recognition as sr
import pyttsx3
import doorman as d

# import doorman from Doorman
# d = Doorman()


# Initialize speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices') # fetching different voices from the system
engine.setProperty('voice', voices[10].id) # setting voice properties
engine.setProperty('rate', 120) # sets speed of speech
driver = d.Doorman()
r = sr.Recognizer()
mic = sr.Microphone()

# set the keyword to be detected
keyword = "doorman"

# set greeting
greeting = "I am your doorman. How can I help you?"
# define a callback function to process the detected text
def callback(recognizer, audio):
    try:
        # use the Sphinx recognizer to convert speech to text
        text = recognizer.recognize_sphinx(audio, keyword_entries=[(keyword, 0.5)])
        engine.say(greeting)
        engine.runAndWait()

        # listen for the next sentence
        audio = recognizer.listen(mic)
        sentence = recognizer.recognize_google(audio)
        print("Doorman recieved msg with content: ", sentence)

        # here, we will pass sentence to the doorman class, and that will return a response in the form of a string
        response, embeddings = driver.handleRequest(sentence)
        engine.say(response)
        engine.runAndWait()

        if response == "Please specify the name of the person you want to add.":
            engine.say(response)
            engine.runAndWait()
            audio = recognizer.listen(mic)
            sentence = recognizer.recognize_google(audio)
            print("Name: ", sentence)
            response = driver.add_new_user(sentence, embeddings)
            engine.say(response)
            engine.runAndWait()


        # this can be commented out once the nlp class is implemented

        # stop listening for more input
        #stop_listening(wait_for_stop=False)

    except sr.UnknownValueError:
        pass

# start listening in the background
stop_listening = r.listen_in_background(mic, callback)

# keep the main thread alive
def main():
    while True:
        pass

if __name__ == '__main__':
    main()
