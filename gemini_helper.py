import os
from google import genai
from google.genai import types
import json

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def review_code(code, language, profession="student"):
    context = get_profession_context(profession)
    prompt = f"""You are a code reviewer for a {profession}. {context}
    
Analyze this {language} code and provide:
1. Code quality assessment
2. Potential bugs or issues
3. Security concerns
4. Performance suggestions
5. Best practices recommendations

Code:
```{language}
{code}
```

Provide a detailed review."""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt
    )
    return response.text if response.text else "Unable to review code at this time."

def explain_code(code, language, profession="student"):
    context = get_profession_context(profession)
    prompt = f"""You are a code explainer for a {profession}. {context}
    
Explain this {language} code in detail:
1. What the code does
2. How it works (step by step)
3. Key concepts used
4. Use cases and applications

Code:
```{language}
{code}
```

Provide a clear, detailed explanation."""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt
    )
    return response.text if response.text else "Unable to explain code at this time."

def compile_check(code, language, profession="student"):
    context = get_profession_context(profession)
    prompt = f"""You are a code compiler checker for a {profession}. {context}
    
Analyze this {language} code for compilation/execution issues:
1. Syntax errors
2. Logic errors
3. Runtime errors
4. Dependencies needed
5. Expected output

Code:
```{language}
{code}
```

Provide detailed compilation check results."""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt
    )
    return response.text if response.text else "Unable to check code at this time."

def answer_question(question, code=None, language=None):
    if code and language:
        prompt = f"""Answer this question about the following {language} code:

Code:
```{language}
{code}
```

Question: {question}

Provide a detailed, helpful answer."""
    else:
        prompt = f"""Answer this coding question: {question}

Provide a detailed, helpful answer with code examples if relevant."""
    
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

def get_dictionary_content(language, category):
    prompt = f"""Provide {category} code templates and snippets for {language}.

Category: {category}
Language: {language}

Provide practical, working code examples with explanations."""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt
    )
    return response.text if response.text else f"No {category} templates available for {language}."
