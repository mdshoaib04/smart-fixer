import os
from google import genai
from google.genai import types
import json

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def review_code(code, language, profession="student"):
    context = get_profession_context(profession)
    prompt = f"""You are a code reviewer for a {profession}. {context}
    
Analyze this {language} code CONCISELY:
1. Code Quality (1-2 sentences)
2. Bugs/Issues (if any, max 3)
3. Security (if concerns exist, brief)
4. Performance (key suggestion)
5. Best Practice (1 main tip)

Code:
```{language}
{code}
```

Keep response short and focused - only mention what's necessary."""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt
    )
    return response.text if response.text else "Unable to review code at this time."

def explain_code(code, language, profession="student"):
    context = get_profession_context(profession)
    prompt = f"""You are a code explainer for a {profession}. {context}
    
Explain this {language} code BRIEFLY:
1. Purpose (1 sentence)
2. How it works (3-5 key steps)
3. Main concepts (2-3 points)
4. Use case (1 example)

Code:
```{language}
{code}
```

Keep explanation concise and easy to understand."""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt
    )
    return response.text if response.text else "Unable to explain code at this time."

def compile_check(code, language, profession="student"):
    context = get_profession_context(profession)
    prompt = f"""You are a code compiler for {language}. 

Execute this {language} code and provide ONLY the output result.

Code:
```{language}
{code}
```

Return ONLY what this code will print/output when run. If there are errors, show the error message. Do not explain how to run it."""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt
    )
    return response.text if response.text else "Unable to compile code at this time."

def answer_question(question, code=None, language=None):
    if code and language:
        prompt = f"""Answer this question about the {language} code:

Code:
```{language}
{code}
```

Question: {question}

Answer BRIEFLY in 2-3 sentences with key points only."""
    else:
        prompt = f"""Answer this coding question: {question}

Provide a CONCISE answer (2-4 sentences) with code example if needed."""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt
    )
    return response.text if response.text else "Unable to answer at this time."

def translate_code(code, from_lang, to_lang):
    prompt = f"""Translate this code from {from_lang} to {to_lang}.
    
Maintain the same logic and functionality.

Original {from_lang} code:
```{from_lang}
{code}
```

Provide the translated {to_lang} code with explanations of any significant changes."""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt
    )
    return response.text if response.text else "Unable to translate code at this time."

def detect_language(code):
    prompt = f"""Detect the programming language of this code. Return only the language name (e.g., Python, JavaScript, C++, Java, etc).

Code:
```
{code}
```

Return ONLY the language name, nothing else."""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt
    )
    return response.text.strip() if response.text else "Unknown"

def get_profession_context(profession):
    contexts = {
        "student": "Focus on learning and understanding. Explain concepts clearly.",
        "professor": "Provide academic insights and teaching perspectives.",
        "frontend": "Focus on UI/UX, performance, and browser compatibility.",
        "backend": "Focus on server logic, databases, APIs, and scalability.",
        "software_engineer": "Provide professional, production-ready insights.",
        "data_scientist": "Focus on data processing, algorithms, and analytics.",
        "devops": "Focus on deployment, CI/CD, containers, and infrastructure.",
        "competitive_programmer": "Focus on algorithmic efficiency, time/space complexity."
    }
    return contexts.get(profession, "Provide helpful coding insights.")

def get_dictionary_content(language, searchTerm):
    prompt = f"""Provide a SIMPLE, SHORT, and EASY TO UNDERSTAND code example for "{searchTerm}" in {language}.

Requirements:
- Code must be the SIMPLEST possible implementation
- Maximum 10-15 lines of code
- Easy for beginners to understand
- Include only essential comments
- Practical and ready to use

Search Term: {searchTerm}
Language: {language}

Return ONLY the code with minimal explanation."""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt
    )
    return response.text if response.text else f"No template found for '{searchTerm}' in {language}."
