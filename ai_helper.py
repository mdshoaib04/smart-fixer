"""
AI Helper Module - Abstraction layer for different AI providers
Supports Gemini, OpenAI, Hugging Face, DeepSeek, OpenRouter, and other providers through a unified interface
"""

import os
from dotenv import load_dotenv
import logging
import requests

load_dotenv()

# Global AI client
ai_client = None
ai_provider = None

def initialize_ai_client():
    """Initialize the appropriate AI client based on environment variables"""
    global ai_client, ai_provider
    
    # Check for different API keys to determine provider
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    huggingface_key = os.environ.get("HUGGINGFACE_API_KEY")
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    
    try:
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            # Initialize Gemini
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            
            # Auto-detect the first available model
            print("🔍 Detecting available Gemini models...")
            models = genai.list_models()
            available_models = [m for m in models if 'generateContent' in m.supported_generation_methods]
            
            if available_models:
                # Try models in order of preference
                model_preferences = [
                    'models/gemini-1.5-pro',
                    'models/gemini-1.5-flash', 
                    'models/gemini-pro',
                    'models/gemini-1.0-pro'
                ]
                
                chosen_model = None
                for preferred in model_preferences:
                    for available in available_models:
                        if preferred in available.name:
                            chosen_model = available.name
                            break
                    if chosen_model:
                        break
                
                # If no preferred model found, use the first available
                if not chosen_model:
                    chosen_model = available_models[0].name
                
                # Remove 'models/' prefix if present
                model_name = chosen_model.replace('models/', '')
                ai_client = genai.GenerativeModel(model_name)
                ai_provider = "gemini"
                print(f"✅ Gemini AI configured successfully with model: {model_name}")
                return True
            else:
                print("❌ No compatible Gemini models found for generateContent")
                
        elif openai_key and openai_key != "your_openai_api_key_here":
            # Initialize OpenAI
            from openai import OpenAI
            ai_client = OpenAI(api_key=openai_key)
            ai_provider = "openai"
            print("✅ OpenAI configured successfully")
            return True
            
        elif huggingface_key and huggingface_key != "your_huggingface_api_key_here":
            # Initialize Hugging Face
            ai_client = {
                "api_key": huggingface_key,
                "base_url": "https://api-inference.huggingface.co"
            }
            ai_provider = "huggingface"
            print("✅ Hugging Face configured successfully")
            return True
            
        elif deepseek_key and deepseek_key != "your_deepseek_api_key_here":
            # Initialize DeepSeek
            from openai import OpenAI
            ai_client = OpenAI(
                api_key=deepseek_key,
                base_url="https://api.deepseek.com"
            )
            ai_provider = "deepseek"
            print("✅ DeepSeek configured successfully")
            return True
            
        elif openrouter_key and openrouter_key != "your_openrouter_api_key_here":
            # Initialize OpenRouter
            from openai import OpenAI
            ai_client = OpenAI(
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1"
            )
            ai_provider = "openrouter"
            print("✅ OpenRouter configured successfully")
            return True
            
        else:
            print("⚠️  No AI API key configured!")
            print("📝 Configure one of these in your .env file:")
            print("   GEMINI_API_KEY='your_gemini_key_here'")
            print("   OPENAI_API_KEY='your_openai_key_here'")
            print("   HUGGINGFACE_API_KEY='your_huggingface_key_here'")
            print("   DEEPSEEK_API_KEY='your_deepseek_key_here'")
            print("   OPENROUTER_API_KEY='your_openrouter_key_here'")
            ai_client = None
            ai_provider = None
            return False
            
    except Exception as e:
        print(f"⚠️  Error configuring AI client: {e}")
        ai_client = None
        ai_provider = None
        return False

def test_ai_connection():
    """Test the AI API connection"""
    if not ai_client:
        return "❌ AI client not initialized"
    
    try:
        if ai_provider == "gemini":
            response = ai_client.generate_content("Hello! Please respond with 'AI is working' to confirm connection.")
            return f"✅ {ai_provider.upper()} AI is working! Response: {response.text}"
        elif ai_provider in ["openai", "deepseek", "openrouter"]:
            model = "gpt-3.5-turbo"
            if ai_provider == "openrouter":
                model = "openai/gpt-3.5-turbo"  # Default OpenRouter model
            elif ai_provider == "deepseek":
                model = "deepseek-chat"
                
            response = ai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hello! Please respond with 'AI is working' to confirm connection."}],
                max_tokens=50
            )
            return f"✅ {ai_provider.upper()} AI is working! Response: {response.choices[0].message.content}"
        elif ai_provider == "huggingface":
            headers = {"Authorization": f"Bearer {ai_client['api_key']}"}
            payload = {
                "inputs": "Hello! Please respond with 'AI is working' to confirm connection.",
                "parameters": {"max_new_tokens": 50}
            }
            response = requests.post(
                f"{ai_client['base_url']}/models/gpt2",
                headers=headers,
                json=payload
            )
            if response.status_code == 200:
                result = response.json()
                return f"✅ {ai_provider.upper()} AI is working! Response: {result[0]['generated_text']}"
            else:
                return f"❌ {ai_provider.upper()} AI connection failed: {response.text}"
        else:
            return "❌ Unsupported AI provider"
    except Exception as e:
        return f"❌ AI Connection test failed: {e}"

def generate_content(prompt, max_tokens=None):
    """Generate content using the configured AI provider"""
    if not ai_client:
        return "⚠️ AI client not initialized. Please configure an API key."
    
    try:
        if ai_provider == "gemini":
            response = ai_client.generate_content(prompt)
            return response.text if response.text else "Unable to generate content at this time."
        elif ai_provider in ["openai", "deepseek", "openrouter"]:
            model = "gpt-3.5-turbo"
            if ai_provider == "openrouter":
                model = "openai/gpt-3.5-turbo"  # Default OpenRouter model
            elif ai_provider == "deepseek":
                model = "deepseek-chat"
                
            kwargs = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            }
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
                
            response = ai_client.chat.completions.create(**kwargs)
            return response.choices[0].message.content if response.choices[0].message.content else "Unable to generate content at this time."
        elif ai_provider == "huggingface":
            headers = {"Authorization": f"Bearer {ai_client['api_key']}"}
            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": max_tokens or 200}
            }
            # Use a general model endpoint - in production, you might want to specify a specific model
            response = requests.post(
                f"{ai_client['base_url']}/models/gpt2",
                headers=headers,
                json=payload
            )
            if response.status_code == 200:
                result = response.json()
                return result[0]['generated_text'] if result and len(result) > 0 else "Unable to generate content at this time."
            else:
                return f"Error with Hugging Face API: {response.text}"
        else:
            return "❌ Unsupported AI provider"
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "rate" in error_msg.lower() or "limit" in error_msg.lower():
            return "⚠️ API quota exceeded. Please wait a moment and try again, or upgrade to a paid plan for unlimited access."
        elif "403" in error_msg or "permission" in error_msg.lower():
            return "⚠️ API access denied. Please check your API key permissions."
        else:
            return f"Error generating content: {error_msg}. Please check your API key configuration."

# Initialize the AI client when module is imported
initialize_ai_client()