
import os
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def list_models():
    if not GEMINI_API_KEY:
        print("No GEMINI_API_KEY found.")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json()
            print("Available Models:")
            for model in models.get('models', []):
                print(f"- {model['name']}")
        else:
            print(f"Error listing models (Code {response.status_code}): {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
