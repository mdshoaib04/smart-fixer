
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def list_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            with open("models_list_utf8.txt", "w", encoding="utf-8") as f:
                f.write("Available Models:\n")
                for model in data.get('models', []):
                    f.write(f"- {model['name']} ({model.get('displayName', 'No display name')})\n")
                    f.write(f"  Supported methods: {model.get('supportedGenerationMethods', [])}\n")
            print("Models list written to models_list_utf8.txt")
        else:
            print(f"Error listing models: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found")
    else:
        list_models()
