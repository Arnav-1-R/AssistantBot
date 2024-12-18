import requests
import time
import pyttsx3
import speech_recognition as sr
import datetime
import os
import platform
import pywhatkit
import wikipedia
from googlesearch import search
import webbrowser

# Initialize TTS engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')

def set_voice(voice_name):
    for voice in voices:
        if voice_name.lower() in voice.name.lower():
            engine.setProperty('voice', voice.id)
            return True
    return False

# Set voice to Zara (if available)
if not set_voice("Zara"):
    print("Zara voice not found, using default voice.")

# Detect platform
current_platform = platform.system().lower()

# Text to Speech
def speak(audio, emotion=None):
    if emotion == "happy":
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 1)
    elif emotion == "sad":
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.8)
    elif emotion == "excited":
        engine.setProperty('rate', 210)
        engine.setProperty('volume', 1)
    elif emotion == "concerned":
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
    else:
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)

    engine.say(audio)
    print(audio)
    engine.runAndWait()

# Speech recognition
def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}")
            return query.lower()

        except sr.RequestError:
            speak("There seems to be an issue with the speech recognition service.", "concerned")
            return "none"

# Wishing the user based on time of day
def wish():
    hour = int(datetime.datetime.now().hour)

    if hour >= 0 and hour < 12:
        speak("Good morning, sir!", "happy")
    elif hour >= 12 and hour < 18:
        speak("Good afternoon, sir!", "happy")
    else:
        speak("Good evening, sir!", "calm")

    speak("How can I assist you today?", "excited")

# Hugging Face API Integration
HUGGING_FACE_API_KEY = "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"  # Replace with your API token
MODEL_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
chat_history = []  # Store chat history as a list of strings

def chatbot_response_huggingface(query):
    global chat_history

    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}
    conversation = "\n".join(chat_history[-5:] + [query])  # Limit chat history
    payload = {"inputs": conversation}

    for attempt in range(5):  # Retry up to 5 times
        try:
            response = requests.post(MODEL_URL, headers=headers, json=payload)
            if response.status_code == 503:  # Model is loading
                print("Model is loading. Retrying in a few seconds...")
                time.sleep(10)
            elif response.status_code == 200:
                chatbot_output = response.json()
                response_text = chatbot_output.get("generated_text", "I am not sure how to respond.")
                chat_history.append(query)
                chat_history.append(response_text)
                return response_text
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"An error occurred: {e}"

    return "The model is taking too long to load. Please try again later."

def clear_chat_history():
    global chat_history
    chat_history.clear()
    speak("Chat history cleared. Let's start fresh!", "excited")

# Command execution
def execute_command(query):
    if "clear chat" in query:
        clear_chat_history()

    elif "play music" in query:
        speak("Which song would you like to play?", "excited")
        song = takecommand()
        if song != "none":
            speak(f"Playing {song} on YouTube...", "happy")
            pywhatkit.playonyt(song)
            time.sleep(5)
            speak("Music is playing. Let me know when you need me again.", "happy")
            input("Press Enter to continue...")
        else:
            speak("Sorry, I couldn't hear the song name. Please try again.", "concerned")

    elif "search wikipedia" in query or "wikipedia" in query:
        search_query = query.replace("search wikipedia for", "").replace("wikipedia", "").strip()
        if search_query:
            fetch_wikipedia_info(search_query)
        else:
            speak("What would you like me to search on Wikipedia?", "excited")
            search_query = takecommand()
            fetch_wikipedia_info(search_query)

    elif "search google" in query or "google" in query:
        search_query = query.replace("search google for", "").replace("google", "").strip()
        if search_query:
            fetch_google_search(search_query)
        else:
            speak("What would you like me to search on Google?", "excited")
            search_query = takecommand()
            fetch_google_search(search_query)


# Fetch Information from Wikipedia
def fetch_wikipedia_info(query):
    try:
        speak("Searching Wikipedia...", "excited")
        result = wikipedia.summary(query, sentences=2)
        print(result)
        speak(result, "happy")
    except wikipedia.exceptions.DisambiguationError as e:
        speak("This topic has multiple results. Please narrow your query.", "concerned")
        print(e.options)
    except wikipedia.exceptions.PageError:
        speak("Sorry, I could not find any information on that topic.", "concerned")
    except Exception as e:
        speak("An error occurred while fetching the information.", "concerned")
        print(f"Error: {e}")

# Fetch Information Using Google Search
def fetch_google_search(query):
    try:
        speak("Searching Google...", "excited")
        search_results = list(search(query, num_results=3))  # Convert search results to a list
        for i, result in enumerate(search_results):
            print(f"Result {i+1}: {result}")
            if i == 0:  # Announce the first result
                top_result = result
                speak(f"Here's the top result: {top_result}", "happy")

        # Ask user if they want to open the link
        speak("Would you like me to open the top result?", "excited")
        response = takecommand()

        if "yes" in response or "yeah" in response:
            webbrowser.open(top_result)
            speak("Opening the top result for you.", "excited")
        else:
            speak("Okay, let me know if you need anything else.", "calm")

    except Exception as e:
        speak("An error occurred while fetching Google search results.", "concerned")
        print(f"Error: {e}")


if __name__ == "__main__":
    wish()
    while True:
        query = takecommand()

        if query != "none":
            # Check for specific commands before chatbot response
            execute_command(query)

            # Chatbot-like responses
            response = chatbot_response_huggingface(query)
            speak(response)
