import requests
import pywhatkit
from huggingface_hub import InferenceApi  # Example: Hugging Face Inference API
from googlesearch import search

# Hugging Face Model
HUGGING_FACE_API_KEY = "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"
hugging_face_model = InferenceApi("facebook/blenderbot-400M-distill", token={HUGGING_FACE_API_KEY})

# Function for conversational response
def conversational_response(query):
    payload = {"inputs": query}
    try:
        response = hugging_face_model(payload)
        return response.get('generated_text', "Sorry, I couldn't understand that.")
    except Exception as e:
        return f"Error with Hugging Face API: {e}"

# Function for Google Search
def search_google(query):
    try:
        search_results = list(search(query, num_results=5))
        return search_results if search_results else "No results found."
    except Exception as e:
        return f"Error with Google Search: {e}"

# Function for playing music
def play_music(song):
    try:
        pywhatkit.playonyt(song)
        return f"Playing {song} on YouTube."
    except Exception as e:
        return f"Error playing music: {e}"

# Routing function
def handle_query(query):
    if "search" in query.lower():
        return search_google(query.replace("search", "").strip())
    elif "play music" in query.lower():
        song = query.replace("play music", "").strip()
        return play_music(song)
    else:
        return conversational_response(query)

# Main Program
while True:
    user_input = input("You: ")  # Replace with speech-to-text function if needed
    response = handle_query(user_input)
    print(f"Bot: {response}")
