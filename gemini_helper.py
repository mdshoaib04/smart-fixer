"""
Gemini Helper Module - Legacy compatibility layer
This module maintains backward compatibility with existing code
while using the new AI abstraction layer
"""

import os
from ai_helper import ai_client, ai_provider, generate_content, test_ai_connection

def test_gemini_connection():
    """Test the AI API connection (maintains backward compatibility)"""
    return test_ai_connection()

def review_code(code, language, profession="student"):
    """Review code using the configured AI provider"""
    if not ai_client:
        return "⚠️ AI API key not configured. Please add your API key to the .env file to enable AI features."
    
    try:
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
        
        return generate_content(prompt)
    except Exception as e:
        return f"Error analyzing code: {str(e)}. Please check your API key configuration."

def explain_code(code, language, profession="student"):
    """Explain code using the configured AI provider"""
    if not ai_client:
        return "⚠️ AI API key not configured. Please add your API key to the .env file to enable AI features."
    
    try:
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
        
        return generate_content(prompt)
    except Exception as e:
        return f"Error explaining code: {str(e)}. Please check your API key configuration."

def compile_check(code, language, profession="student"):
    """Compile check using the configured AI provider"""
    if not ai_client:
        return "⚠️ AI API key not configured. Please add your API key to the .env file to enable AI features."
    
    try:
        prompt = f"""You are a code compiler for {language}. 

Execute this {language} code and provide ONLY the output result.

Code:
```{language}
{code}
```

Return ONLY what this code will print/output when run. If there are errors, show the error message. Do not explain how to run it."""
        
        return generate_content(prompt)
    except Exception as e:
        return f"Error compiling code: {str(e)}. Please check your API key configuration."

def answer_question(question, code=None, language=None):
    """Answer question using the configured AI provider"""
    if not ai_client:
        return "⚠️ AI API key not configured. Please add your API key to the .env file to enable AI features."
    
    try:
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
        
        return generate_content(prompt)
    except Exception as e:
        return f"Error answering question: {str(e)}. Please check your API key configuration."

def translate_code(code, from_lang, to_lang):
    """Translate code using the configured AI provider"""
    if not ai_client:
        return "⚠️ AI API key not configured. Please add your API key to the .env file to enable AI features."
    
    try:
        prompt = f"""Translate this code from {from_lang} to {to_lang}.
        
Maintain the same logic and functionality.

Original {from_lang} code:
```{from_lang}
{code}
```

Provide the translated {to_lang} code with explanations of any significant changes."""
        
        return generate_content(prompt)
    except Exception as e:
        return f"Error translating code: {str(e)}. Please check your API key configuration."

def detect_language(code):
    """Detect language using the configured AI provider"""
    if not ai_client:
        return "Python"  # Default fallback
    
    try:
        prompt = f"""Detect the programming language of this code. Return only the language name (e.g., Python, JavaScript, C++, Java, etc).

Code:
```
{code}
```

Return ONLY the language name, nothing else."""
        
        result = generate_content(prompt)
        return result.strip() if result else "Unknown"
    except Exception as e:
        print(f"Language detection error: {e}")
        return "Python"  # Default fallback

def get_profession_context(profession):
    """Get profession context for AI prompts"""
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
    """Get dictionary content using the configured AI provider"""
    if not ai_client:
        return "⚠️ AI API key not configured. Please add your API key to the .env file to enable AI features."
    
    try:
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
        
        return generate_content(prompt)
    except Exception as e:
        return f"Error getting dictionary content: {str(e)}. Please check your API key configuration."