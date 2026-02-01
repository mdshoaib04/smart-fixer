"""
AI Models Module - Full Local Integration
Uses GPT4All for all coding tasks, removing external API dependencies.
"""

import logging
import re
from typing import Optional, Dict, List, Tuple
from ai_helper import generate_content

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_language(code: str) -> str:
    """Detect programming language from code using heuristics or local AI"""
    if not code or len(code.strip()) < 5:
        return "python"
    
    code_lower = code.lower()
    
    # Heuristics for basic languages
    if any(k in code_lower for k in ['<!doctype html>', '<html>', '<body>', '<div']): return "html"
    if any(k in code_lower for k in ['body {', '.class {', '#id {', 'margin:']): return "css"
    if any(k in code_lower for k in ['def ', 'import ', 'if __name__']): return "python"
    if any(k in code_lower for k in ['function ', 'const ', 'let ', 'console.log']): return "javascript"
    if any(k in code_lower for k in ['public class', 'public static void']): return "java"
    if any(k in code_lower for k in ['#include <iostream>', 'std::cout']): return "cpp"
    if any(k in code_lower for k in ['#include <stdio.h>', 'printf(']): return "c"
    
    # Local AI Fallback
    prompt = f"Identify the programming language of this code. Return ONLY the language name (e.g., python, javascript, cpp, java).\n\nCode:\n{code[:500]}"
    result = generate_content(prompt, max_tokens=10)
    if result:
        lang = result.strip().lower().split('\n')[0].replace('.', '')
        return lang
    
    return "python"

def generate_code(prompt: str, language: str = "python") -> str:
    """Generate the SMALLEST and SIMPLEST code using local AI"""
    lang = language.lower()
    
    full_prompt = f"Write short {lang} code for: {prompt}. Return code ONLY."
    
    result = generate_content(full_prompt, max_tokens=250)
    if result:
        # Clean markdown
        result = re.sub(r'```\w*\n?', '', result)
        result = re.sub(r'```\s*$', '', result)
        return result.strip()
            
    return f"# Error generating {lang} code locally for: {prompt}."

def translate_code(code: str, to_lang: str, from_lang: str = None) -> str:
    """Translate code using local AI"""
    if not from_lang:
        from_lang = detect_language(code)
    
    from_lang = from_lang.lower()
    to_lang = to_lang.lower()
    
    if from_lang == to_lang:
        return code
        
    prompt = f"""Translate this {from_lang} code to {to_lang}.
    PRESERVE LOGIC. Keep it concise.
    Return ONLY the translated code. No explanations.
    
    Original {from_lang}:
    {code}
    
    {to_lang} code:"""
    
    result = generate_content(prompt, max_tokens=500)
    if result:
        result = re.sub(r'```\w*\n?', '', result)
        result = re.sub(r'```\s*$', '', result)
        return result.strip()
            
    return f"// Local translation failed from {from_lang} to {to_lang}."

def review_code(code: str, language: str) -> str:
    """Review code using local AI"""
    lang = language.lower()
    
    prompt = f"""Review this {lang} code for errors and improvements.
    Be concise. Use bullet points.
    
    Code:
    {code}"""
    
    result = generate_content(prompt, max_tokens=400)
    return result.strip() if result else "• Local AI review unavailable."

def explain_code(code: str, language: str, role: str = "student") -> str:
    """Explain code using local AI"""
    lang = language.lower()
    role = role.lower()
    
    prompt = f"""Explain this {lang} code as a {role} in simple, short bullet points.
    
    Code:
    {code}"""
    
    result = generate_content(prompt, max_tokens=500)
    return result.strip() if result else f"Explanation ({role}):\n• Local AI unavailable."

def ask_question(question: str, code: str = None, language: str = "python") -> str:
    """Answer coding questions using local AI"""
    context = f"\n\nContext Code ({language}):\n{code}" if code else ""
    
    prompt = f"""Answer this coding question concisely.
    Question: {question}{context}
    
    Answer:"""
    
    result = generate_content(prompt, max_tokens=400)
    return result.strip() if result else "Local AI module unavailable."

def initialize_models():
    """Initialization handled by ai_helper"""
    logger.info("Local AI models module loaded.")

# Initialize on import
initialize_models()
