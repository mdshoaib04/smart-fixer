
import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

def test_model(model_name, stream=False):
    print(f"\n--- Testing Model: {model_name} (Stream={stream}) ---")
    if not model_name.startswith("models/"):
        model_id = f"models/{model_name}"
    else:
        model_id = model_name
        
    method = "streamGenerateContent" if stream else "generateContent"
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_id}:{method}?key={GEMINI_API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": "Write a long story about a brave knight. Minimum 500 words."}]
        }],
        "generationConfig": {
            "maxOutputTokens": 1000,
            "temperature": 0.7
        }
    }
    
    try:
        start_time = time.time()
        print(f"Sending request to {url}...")
        response = requests.post(url, headers=headers, json=payload, stream=stream, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            if stream:
                print("Streaming response...")
                chunk_count = 0
                for line in response.iter_lines():
                    if line:
                        chunk_count += 1
                        # print(f"Chunk {chunk_count}: {line[:50]}...")
                print(f"Received {chunk_count} chunks.")
            else:
                data = response.json()
                print("Success! Response received.")
            
            duration = time.time() - start_time
            print(f"Total Duration: {duration:.2f}s")
            return True
        else:
            print(f"Error Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found in .env")
    else:
        print(f"API Key found (length: {len(GEMINI_API_KEY)})")
        
        # Test configured model with streaming
        print(f"Configured GEMINI_MODEL: {GEMINI_MODEL}")
        test_model(GEMINI_MODEL, stream=True)
        
        # Test fallback models
        test_model("gemini-2.0-flash-exp", stream=True)
        test_model("gemini-1.5-flash", stream=False) # Retest non-stream just in case

