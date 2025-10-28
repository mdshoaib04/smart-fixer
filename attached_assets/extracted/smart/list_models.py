import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    for m in genai.list_models():
        print(m.name)
else:
    print("GEMINI_API_KEY not found in .env file.")