"""
AI Helper Module - Abstraction layer for different AI providers
Supports local inference via GPT4All as requested by the user.
"""

import os
import threading
import time
from dotenv import load_dotenv
import logging
from gpt4all import GPT4All

load_dotenv()

# Global AI client
ai_client = None
ai_provider = "local_gpt4all"
ai_lock = threading.Lock()

def initialize_ai_client():
    """Initialize the local GPT4All model"""
    global ai_client, ai_provider
    
    try:
        # Using Phi-3 which is very fast and great for coding tasks
        model_name = os.environ.get("LOCAL_MODEL_NAME", "Phi-3-mini-4k-instruct.Q4_0.gguf")
        print(f"Initializing local AI module: {model_name}")
        
        # Initialize GPT4All with a safer thread count for stability and speed
        # 4 threads is often the sweet spot for many consumer CPUs
        ai_client = GPT4All(model_name, n_threads=4)
        print(f"Local AI module '{model_name}' ready with optimized settings!")
        return True
            
    except Exception as e:
        print(f"Error configuring local AI client: {e}")
        ai_client = None
        return False

def test_ai_connection():
    """Test the local AI connection"""
    if not ai_client:
        return "[Error] Local AI module not initialized"
    
    try:
        response = generate_content("Hello! Please respond with 'AI is working' to confirm connection.", max_tokens=50)
        return f"[Success] Local AI is working! Response: {response}"
    except Exception as e:
        return f"[Error] Local AI test failed: {e}"

def generate_content(prompt, max_tokens=200):
    """Generate content using the local GPT4All model"""
    if not ai_client:
        # Try to initialize if not already
        if not initialize_ai_client():
            return "Local AI module not initialized and failed to start."
    
    try:
        print(f"Generating content locally for prompt: {prompt[:50]}...")
        with ai_lock:
            start_gen = time.time()
            # Restore chat_session for stability and clearer context
            with ai_client.chat_session():
                response = ai_client.generate(
                    prompt, 
                    max_tokens=max_tokens, 
                    temp=0.1 # Slight temp for better code variety
                )
            duration = time.time() - start_gen
            print(f"Generation took: {duration:.2f} seconds")
            return response.strip() if response else "Unable to generate content locally."
    except Exception as e:
        error_msg = str(e)
        return f"Error generating content locally: {error_msg}."

# Initialize the AI client when module is imported
# This ensures the model is loaded and ready for immediate use
initialize_ai_client() 
