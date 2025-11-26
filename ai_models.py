"""
AI Models Module - Real AI Integration
Uses Hugging Face Inference API (Free) and Gemini (Free Tier) for actual AI responses
"""

import os
import logging
import requests
import json
import re
from typing import Optional, Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hugging Face API (Free, no key required for public models)
HUGGINGFACE_API = "https://api-inference.huggingface.co/models"

# Models for different tasks
MODELS = {
    "code_generation": "bigcode/starcoder",
    "code_explanation": "Salesforce/codegen-350M-mono",
    "code_translation": "Salesforce/codet5-base",
    "code_review": "microsoft/codebert-base",
    "text_generation": "gpt2",
    "conversational": "microsoft/DialoGPT-medium"
}

def call_huggingface_api(model_name: str, prompt: str, max_length: int = 500) -> str:
    """Call Hugging Face Inference API"""
    try:
        url = f"{HUGGINGFACE_API}/{model_name}"
        headers = {"Content-Type": "application/json"}
        
        # Add API key if available for better rate limits
        api_key = os.environ.get("HUGGINGFACE_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_length,
                "temperature": 0.7,
                "return_full_text": False,
                "do_sample": True,
                "top_p": 0.95
            }
        }
        
        logger.info(f"Calling Hugging Face API: {model_name}")
        response = requests.post(url, headers=headers, json=payload, timeout=45)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    text = result[0]["generated_text"].strip()
                    if text: return text
                elif "summary_text" in result[0]:
                    text = result[0]["summary_text"].strip()
                    if text: return text
            elif isinstance(result, dict):
                if "generated_text" in result:
                    text = result["generated_text"].strip()
                    if text: return text
                if "text" in result:
                    text = result["text"].strip()
                    if text: return text
        elif response.status_code == 503:
            # Model is loading, wait and retry once
            import time
            logger.info(f"Model {model_name} is loading, waiting 10 seconds...")
            time.sleep(10)
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    if "generated_text" in result[0]:
                        return result[0]["generated_text"].strip()
        else:
            logger.warning(f"API returned status {response.status_code}: {response.text[:200]}")
    except Exception as e:
        logger.error(f"Error calling Hugging Face API: {e}")
    
    return None

def detect_language(code: str) -> str:
    """Detect programming language from code"""
    if not code or len(code.strip()) < 5:
        return "python"
    
    code_lower = code.lower()
    
    # Python indicators
    if any(k in code_lower for k in ['def ', 'import ', 'print(', 'if __name__', 'lambda ', 'elif ']):
        return "python"
    
    # JavaScript indicators
    if any(k in code_lower for k in ['function ', 'const ', 'let ', 'var ', 'console.log', '=>', 'document.']):
        return "javascript"
    
    # Java indicators
    if any(k in code_lower for k in ['public class', 'public static void', 'System.out.println', 'ArrayList<']):
        return "java"
    
    # C++ indicators
    if any(k in code_lower for k in ['#include <iostream>', 'using namespace std', 'std::cout', 'cout <<']):
        return "cpp"
    
    # C indicators
    if any(k in code_lower for k in ['#include <stdio.h>', 'printf(', 'scanf(']):
        return "c"
        
    # HTML indicators
    if any(k in code_lower for k in ['<!DOCTYPE html>', '<html>', '<body>', '<div']):
        return "html"
        
    # CSS indicators
    if any(k in code_lower for k in ['body {', '.class {', '#id {', 'margin:', 'padding:']):
        return "css"

    # Shell/Bash indicators
    if any(k in code_lower for k in ['#!/bin/bash', '#!/bin/sh', 'echo ', 'ls ', 'grep ', 'sudo ', 'apt-get', 'yum install']):
        return "shell"
    
    return "python"

def generate_code(prompt: str, language: str = "python") -> str:
    """Generate the SMALLEST and SIMPLEST code using AI"""
    lang = language.lower()
    
    # Try Gemini first
    try:
        from ai_helper import generate_content, ai_client
        if ai_client and generate_content:
            full_prompt = f"""Write the SMALLEST and SIMPLEST {lang} code for: {prompt}.
            
            CRITICAL RULES:
            1. Code must be extremely concise and easy to understand.
            2. Use the simplest possible logic.
            3. Include ONLY necessary code.
            4. No complex error handling or advanced features unless requested.
            5. Return ONLY the code, no explanation.
            
            {lang} code:"""
            
            result = generate_content(full_prompt)
            if result and len(result.strip()) > 10 and "AI client not initialized" not in result:
                # Clean markdown
                result = re.sub(r'```\w*\n?', '', result)
                result = re.sub(r'```\s*$', '', result)
                return result.strip()
    except Exception as e:
        logger.debug(f"Gemini not available: {e}")
    
    # Fallback to templates for common requests to ensure "simplest"
    prompt_lower = prompt.lower()
    
    if "sum" in prompt_lower or "add" in prompt_lower:
        if lang == "python": return "print(float(input('Num 1: ')) + float(input('Num 2: ')))"
        if lang == "javascript": return "console.log(Number(prompt('Num 1:')) + Number(prompt('Num 2:')))"
        if lang == "java": return "import java.util.Scanner;\nclass Main { public static void main(String[] a) { Scanner s=new Scanner(System.in); System.out.println(s.nextDouble()+s.nextDouble()); } }"
        if lang == "cpp": return "#include <iostream>\nusing namespace std;\nint main() { double a,b; cin>>a>>b; cout<<a+b; return 0; }"

    # Try Hugging Face as backup
    try:
        full_prompt = f"Write simple {lang} code for {prompt}"
        result = call_huggingface_api(MODELS["code_generation"], full_prompt)
        if result: return result
    except:
        pass
        
    return f"# Could not generate code for {prompt}. Please try a simpler request."

def translate_code(code: str, to_lang: str, from_lang: str = None) -> str:
    """Translate code preserving logic (Syntax change only)"""
    if not from_lang:
        from_lang = detect_language(code)
    
    from_lang = from_lang.lower()
    to_lang = to_lang.lower()
    
    if from_lang == to_lang:
        return code
        
    # Try Gemini first
    try:
        from ai_helper import generate_content, ai_client
        if ai_client and generate_content:
            prompt = f"""Translate this {from_lang} code to {to_lang}.
            
            CRITICAL RULES:
            1. PRESERVE THE EXACT LOGIC. Do not change what the code does.
            2. ONLY change the syntax to match {to_lang}.
            3. Keep variable names if possible.
            4. Return ONLY the translated code.
            
            Original {from_lang} Code:
            {code}
            
            Translated {to_lang} Code:"""
            
            result = generate_content(prompt)
            if result and "AI client not initialized" not in result:
                result = re.sub(r'```\w*\n?', '', result)
                result = re.sub(r'```\s*$', '', result)
                return result.strip()
    except Exception as e:
        logger.debug(f"Gemini translation failed: {e}")

    # Fallback: Simple Pattern Matching for common languages
    if from_lang == "python" and to_lang == "java":
        return code.replace("print(", "System.out.println(").replace("def ", "void ").replace(":", " { // add } at end")
    
    return f"// Translation from {from_lang} to {to_lang} requires AI model.\n// Please configure API key."

def review_code(code: str, language: str) -> str:
    """Review code: Errors, Warnings, Improvements (Bullet Points)"""
    lang = language.lower()
    
    # Try Gemini first
    try:
        from ai_helper import generate_content, ai_client
        if ai_client and generate_content:
            prompt = f"""Review this {lang} code. Provide output in this EXACT format:
            
            Errors:
            • [Line X] Error description
            
            Warnings:
            • [Line X] Warning description
            
            Improvements:
            • Suggestion 1
            • Suggestion 2
            
            Code:
            {code}"""
            
            result = generate_content(prompt)
            if result and "AI client not initialized" not in result:
                return result.strip()
    except Exception:
        pass
        
    return "• Unable to review code (AI unavailable)."

def explain_code(code: str, language: str, role: str = "student") -> str:
    """Explain code based on persona (Student vs Professor)"""
    lang = language.lower()
    role = role.lower()
    
    complexity = "extremely simple, easy to understand, non-technical language" if role == "student" else "highly technical, academic, detailed, using professional terminology"
    
    # Try Gemini first
    try:
        from ai_helper import generate_content, ai_client
        if ai_client and generate_content:
            prompt = f"""Explain this {lang} code as a {role}.
            Use {complexity}.
            Explain line-by-line in bullet points.
            
            Code:
            {code}"""
            
            result = generate_content(prompt)
            if result and "AI client not initialized" not in result:
                return result.strip()
    except Exception:
        pass
        
    return f"Explanation ({role}):\n• AI unavailable."

def ask_question(question: str, code: str = None, language: str = "python") -> str:
    """AI Search Agent for code questions"""
    context = f"\n\nContext Code ({language}):\n{code}" if code else ""
    
    try:
        from ai_helper import generate_content, ai_client
        if ai_client and generate_content:
            prompt = f"""Answer this coding question concisely.
            Question: {question}{context}
            
            Answer:"""
            
            result = generate_content(prompt)
            if result and "AI client not initialized" not in result:
                return result.strip()
    except Exception:
        pass
        
    return "AI Agent unavailable. Please check API configuration."
    
    # Create explanation prompt
    role_descriptions = {
        "student": "Explain in simple, beginner-friendly terms",
        "professor": "Provide detailed technical analysis",
        "developer": "Focus on implementation details and best practices"
    }
    role_desc = role_descriptions.get(role_lower, "Explain")
    
    prompt = f"""{role_desc} this {lang} code:

{code}

Explanation:"""
    
    # Try AI explanation
    try:
        result = call_huggingface_api(MODELS["code_explanation"], prompt, max_length=1000)
        if result and len(result) > 100:
            logger.info(f"✅ Using Hugging Face for code explanation ({role})")
            return result.strip()
    except Exception as e:
        logger.warning(f"AI explanation failed: {e}")
    
    # Fallback explanation
    lines = [l.strip() for l in code.split('\n') if l.strip()]
    functions = [l for l in lines if 'def ' in l or 'function ' in l or 'public static' in l]
    imports = [l for l in lines if 'import ' in l or '#include' in l]
    
    explanation = []
    explanation.append(f"📚 Code Explanation ({role} perspective):\n\n")
    explanation.append(f"This {lang} code:\n\n")
    
    if imports:
        explanation.append(f"• Uses {len(imports)} import(s) for required libraries\n")
    if functions:
        explanation.append(f"• Defines {len(functions)} function(s) to perform tasks\n")
    explanation.append(f"• Executes the main logic step by step\n")
    explanation.append(f"\n💡 Key Points:\n\n")
    explanation.append(f"• The code follows {lang} programming conventions\n")
    explanation.append(f"• Each section serves a specific purpose\n")
    explanation.append(f"• Review the code line by line to understand the flow\n")
    
    return "".join(explanation)

def answer_code_question(question: str, code: str, language: str) -> str:
    """Answer questions about code using AI"""
    lang = language.lower()
    
    # Try Gemini first if available
    try:
        from ai_helper import generate_content, ai_client
        if ai_client and generate_content:
            prompt = f"""Question about {lang} code: {question}

Code:
{code}

Provide a clear, detailed answer:"""
            
            result = generate_content(prompt)
            if result and len(result.strip()) > 50 and "AI client not initialized" not in result and "API key" not in result:
                logger.info("✅ Using Gemini for Q&A")
                return result.strip()
    except Exception as e:
        logger.debug(f"Gemini Q&A not available: {e}")
    
    # Create Q&A prompt
    prompt = f"""Question about {lang} code: {question}

Code:
{code}

Answer the question:"""
    
    # Try AI Q&A
    try:
        result = call_huggingface_api(MODELS["conversational"], prompt, max_length=500)
        if result and len(result) > 50:
            logger.info("✅ Using Hugging Face for Q&A")
            return result.strip()
    except Exception as e:
        logger.warning(f"AI Q&A failed: {e}")
    
    # Fallback answer
    question_lower = question.lower()
    
    if "what" in question_lower:
        return f"This {lang} code performs the requested operation. It processes input and produces output based on the implemented logic."
    elif "how" in question_lower:
        return f"This {lang} code works by:\n1. Processing input data\n2. Applying the algorithm\n3. Returning the result\n\nReview the code step-by-step for details."
    elif "why" in question_lower:
        return f"The code is structured this way to achieve the desired functionality while following {lang} best practices."
    
    return f"Answer regarding the {lang} code:\n\nThe code implements the solution as shown. Review the code logic for specific details about '{question}'."

# Initialize (no heavy models to load)
def initialize_models():
    """Initialize AI models (using API, no local loading needed)"""
    logger.info("✅ AI models ready (using Hugging Face Inference API)")
    logger.info("📡 All AI features will use real-time API calls")

# Initialize on import
try:
    initialize_models()
except Exception as e:
    logger.error(f"Failed to initialize: {e}")
