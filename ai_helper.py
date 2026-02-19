"""
AI Helper Module - Abstraction layer for different AI providers
Supports Cloud AI (Gemini) with automatic fallback to local AI (GPT4All).
"""

import os
import threading
import time
import json
import requests
from dotenv import load_dotenv
import logging
from gpt4all import GPT4All

load_dotenv()

# Global AI client
ai_client = None
ai_provider = "local_gpt4all"
ai_lock = threading.Lock()

# Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# Defaulting to 1.5-flash which is more stable than 3-flash preview during high demand
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash") 
LOCAL_MODEL_NAME = os.environ.get("LOCAL_MODEL_NAME", "Phi-3-mini-4k-instruct.Q4_0.gguf")

def initialize_ai_client():
    """Initialize the local GPT4All model as a fallback"""
    global ai_client, ai_provider
    
    try:
        if ai_client is not None:
            return True
            
        print(f"Initializing local AI fallback: {LOCAL_MODEL_NAME}")
        # Initialize GPT4All with a safer thread count
        ai_client = GPT4All(LOCAL_MODEL_NAME, n_threads=4)
        print(f"Local AI module '{LOCAL_MODEL_NAME}' ready.")
        return True
    except Exception as e:
        print(f"Error configuring local AI client: {e}")
        ai_client = None
        return False

def call_gemini_api(prompt, max_tokens=1000):
    """Call Google Gemini API via REST to avoid library compatibility issues"""
    if not GEMINI_API_KEY:
        return None
        
    model_id = GEMINI_MODEL
    if not model_id.startswith("models/"):
        model_id = f"models/{model_id}"
        
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_id}:generateContent?key={GEMINI_API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.2
        }
    }
    
    max_retries = 3
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"Calling Gemini API ({model_id}), attempt {attempt + 1}...")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    return data['candidates'][0]['content']['parts'][0]['text'].strip()
                return "Empty response from Gemini."
            
            elif response.status_code == 404:
                print(f"Model {model_id} not found. Trying fallback to gemini-1.5-flash...")
                if "gemini-1.5-flash" not in model_id:
                    fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                    resp = requests.post(fallback_url, headers=headers, json=payload, timeout=30)
                    if resp.status_code == 200:
                         data = resp.json()
                         if 'candidates' in data and len(data['candidates']) > 0:
                            return data['candidates'][0]['content']['parts'][0]['text'].strip()
                return None
            
            elif response.status_code == 503 or response.status_code == 429:
                print(f"Gemini API unavailable (Code {response.status_code}): {response.text}")
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    print(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print("Max retries reached for Gemini. Falling back to local AI.")
                    return None
            else:
                print(f"Gemini API error (Code {response.status_code}): {response.text}")
                return None
                
        except requests.exceptions.ConnectionError as e:
            print(f"Gemini connection aborted or failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(base_delay)
                continue
            return None
        except Exception as e:
            print(f"Gemini error: {e}")
            if attempt < max_retries - 1:
                time.sleep(base_delay)
                continue
            return None
            
    return None

def generate_content(prompt, max_tokens=500):
    """Generate content using Gemini (if key exists) with fallback to local GPT4All"""
    
    # Try Gemini first if API key is present
    if GEMINI_API_KEY:
        result = call_gemini_api(prompt, max_tokens=max_tokens)
        if result:
            print("Generated content via Gemini Cloud.")
            return result
            
    # Fallback to local AI
    if not ai_client:
        if not initialize_ai_client():
            return "Both Cloud AI and Local AI are unavailable."
    
    try:
        print(f"Generating content locally (Fallback) for prompt: {prompt[:50]}...")
        with ai_lock:
            start_gen = time.time()
            with ai_client.chat_session():
                response = ai_client.generate(
                    prompt, 
                    max_tokens=max_tokens, 
                    temp=0.1
                )
            duration = time.time() - start_gen
            print(f"Local generation took: {duration:.2f} seconds")
            return response.strip() if response else "Unable to generate content locally."
    except Exception as e:
        return f"Error generating content: {str(e)}."

def test_ai_connection():
    """Test AI connection and report status"""
    status = ""
    
    if GEMINI_API_KEY:
        res = call_gemini_api("Hello, respond with 'Gemini OK'", max_tokens=10)
        if res:
            status += f"[Success] Gemini Cloud AI ({GEMINI_MODEL}) is active.\n"
        else:
            status += "[Failure] Gemini Cloud AI failed or unavailable (503/Quota).\n"
    else:
        status += "[Info] Gemini API key not found in .env. Using local AI only.\n"
        
    if initialize_ai_client():
        status += f"[Success] Local AI module ({LOCAL_MODEL_NAME}) is ready as fallback."
    else:
        status += "[Failure] Local AI module failed to initialize."
        
    return status

# Initialize local fallback on import
initialize_ai_client()
