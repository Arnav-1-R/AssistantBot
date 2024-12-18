import pywhatkit
import requests
from googlesearch import search
from huggingface_hub import InferenceApi  # Example: Hugging Face Inference API

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


    # Stack exchange API (Free for Q&A) technical queries
    def technical_query_response(query):
        try:
            base_url = "https://api.stackexchange.com/2.3/search/advanced"
            params = {
                "order": "desc",
                "sort": "relevance",
                "q": query,
                "site": "stackoverflow"
            }
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data["items"]:
                    results = [item["link"] for item in data["items"][:5]]  # Top 5 results
                    return "Here are some relevant results:\n" + "\n".join(results)
                else:
                    return "No relevant results found."
            else:
                return f"Error: Unable to fetch results ({response.status_code})"
        except Exception as e:
            return f"Error with Stack Exchange API: {e}"


    # Routing function
    def handle_query(query):
        query_lower = query.lower()

        if "search" in query_lower:
            return search_google(query.replace("search", "").strip())
        elif "technical" in query_lower or "solve" in query_lower:
            return technical_query_response(query)
        elif "play music" in query_lower:
            song = query.replace("play music", "").strip()
            return play_music(song)
        else:
            return "I'm sorry, I didn't understand that. Please try again."


    # Main Program
    if __name__ == "__main__":
        while True:
            user_input = input("You: ")
            response = handle_query(user_input)
            print(f"Bot: {response}")
