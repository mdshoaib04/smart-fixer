"""
Code Detection Module - Language-agnostic code pattern detection
Detects if text content is likely programming code based on syntax patterns.
"""

import re
from typing import Tuple, Dict

# Common English words that shouldn't appear frequently in code except in strings/comments
PROSE_KEYWORDS = [
    r'\b(the|and|that|have|for|not|with|you|this|but|his|from|they|say|her|she|will|one|all|would|there|their|what|about|get|which|go|me|when|make|can|like|time|just|him|know|take|person|into|year|your|good|some|could|them|see|other|than|then|now|look|only|come|its|over|think|also|back|after|use|two|how|our|work|first|well|even|new|want|because|any|these|give|most|us)\b'
]

# Structural patterns that indicate code
CODE_PATTERNS = {
    # Keywords common across many languages
    'keywords': [
        r'\b(if|else|elif|while|for|do|switch|case|break|continue|return|try|catch|except|finally|throw|throws)\b',
        r'\b(class|def|function|func|fn|public|private|protected|static|final|const|let|var|async|await)\b',
        r'\b(import|from|export|require|include|using|package|module|namespace)\b',
        r'\b(int|float|double|char|string|bool|boolean|void|null|nil|None|true|false|True|False)\b',
        r'\b(new|this|self|super|extends|implements|interface|abstract|virtual|override|synchronized|volatile)\b',
    ],
    
    # Structural patterns that indicate code
    'structure': [
        r'[\{\}]',  # Braces
        r'\[.*\]',  # Brackets
        r'\(.*\)',  # Parentheses with content
        r';$',  # Semicolons at end of lines
        r'=>',  # Arrow functions
        r'->',  # Arrow/pointer
        r'::',  # Scope resolution
        r'\.\w+\(',  # Method calls
        r'\w+\s*\(.*\)',  # Function calls
        r'^\s{2,}',  # Indentation (2+ spaces)
        r'^\t+',  # Tab indentation
        r'</?\w+>', # HTML/XML tags
    ],
    
    # Operators common in code
    'operators': [
        r'[=!<>]=',  # Comparison
        r'[+\-*/%]=',  # Assignment
        r'&&|\|\|',  # Logical
        r'\+\+|--',  # Inc/Dec
        r'<<|>>',  # Bit shift
        r'===|!==', # JS strict equality
        r'[:=]{1,2}', # Assignment variants
    ],
    
    # Comment patterns
    'comments': [
        r'//.*$',  # C-style
        r'#.*$',  # Python/Shell
        r'/\*.*?\*/',  # Multi-line
        r'""".*?"""',  # Docstrings
        r'<!--.*?-->',  # HTML
    ],
}

# Non-code patterns (things that indicate regular text)
NON_CODE_PATTERNS = [
    r'^[A-Z][a-z].*\s[a-z].*\.\s*$',  # Sentences
    r'^Dear\s+\w+',  # Greetings
    r'[.?!]\s+[A-Z][a-z]',  # Sentence boundaries
    r'\b(I|you|we|they|he|she)\s+\w+(s|ed|ing)?\b', # Subject-verb
    r'\b(a|an|the|this|that|these|those)\s+\w+\b', # Article-noun
]


def count_pattern_matches(text: str, patterns: list) -> int:
    """Count how many patterns match in the text."""
    count = 0
    for pattern in patterns:
        try:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            count += len(matches)
        except re.error:
            continue
    return count


def calculate_code_score(text: str) -> Tuple[float, Dict[str, float]]:
    """
    Calculate a score indicating how likely the text is programming code.
    
    Returns:
        Tuple of (overall_score, breakdown_dict)
        overall_score: 0.0 to 1.0 where 1.0 = definitely code
    """
    if not text or not text.strip():
        return 0.0, {}
    
    text = text.strip()
    lines = text.split('\n')
    total_lines = max(len(lines), 1)
    total_chars = len(text)
    
    if total_chars < 5:
        return 0.0, {}
    
    scores = {}
    
    # Score based on keyword matches - high weight for definitive code keywords
    keyword_matches = count_pattern_matches(text, CODE_PATTERNS['keywords'])
    # Use absolute count with diminishing returns
    scores['keywords'] = min(keyword_matches * 0.15, 0.35)
    
    # Score based on structural patterns - braces, parens, etc.
    structure_matches = count_pattern_matches(text, CODE_PATTERNS['structure'])
    scores['structure'] = min(structure_matches * 0.08, 0.25)
    
    # Score based on operators - common in code
    operator_matches = count_pattern_matches(text, CODE_PATTERNS['operators'])
    scores['operators'] = min(operator_matches * 0.05, 0.1)
    
    # Score based on comments - strong indicator
    comment_matches = count_pattern_matches(text, CODE_PATTERNS['comments'])
    scores['comments'] = min(comment_matches * 0.1, 0.15)
    
    # Score based on language-specific patterns - HIGHEST WEIGHT
    # If we match a language pattern, it's almost certainly code
    lang_scores_raw = {}
    for lang in ['python', 'javascript', 'java', 'c_cpp', 'html', 'css', 'sql', 'shell']:
        if lang in CODE_PATTERNS:
            matches = count_pattern_matches(text, CODE_PATTERNS[lang])
            lang_scores_raw[lang] = matches
    
    # Any language-specific match is a strong signal
    max_lang_matches = max(lang_scores_raw.values()) if lang_scores_raw else 0
    if max_lang_matches >= 2:
        scores['language_specific'] = 0.4  # Strong boost for multiple language matches
    elif max_lang_matches >= 1:
        scores['language_specific'] = 0.25  # Good boost for single language match
    else:
        scores['language_specific'] = 0.0
    
    # Check for very definitive code patterns (instant high score)
    definitive_patterns = [
        r'^\s*def\s+\w+\s*\(',  # Python function
        r'^\s*class\s+\w+',  # Class definition
        r'^\s*function\s+\w+\s*\(',  # JS/PHP function
        r'^\s*public\s+(class|static|void)',  # Java/C# class/method
        r'#include\s*[<"]',  # C/C++ include
        r'^\s*import\s+\w+',  # Import statement
        r'^\s*from\s+\w+\s+import',  # Python from-import
        r'<\w+[^>]*>.*</\w+>',  # HTML tags
        r'SELECT\s+.*\s+FROM\s+\w+',  # SQL query
    ]
    definitive_matches = count_pattern_matches(text, definitive_patterns)
    if definitive_matches > 0:
        scores['definitive'] = min(definitive_matches * 0.2, 0.4)
    else:
        scores['definitive'] = 0.0
    
    # Line-based analysis for code structure
    indented_lines = sum(1 for line in lines if line.startswith('  ') or line.startswith('\t'))
    if total_lines > 1 and indented_lines > 0:
        indent_ratio = indented_lines / total_lines
        scores['indentation'] = indent_ratio * 0.1
    else:
        scores['indentation'] = 0.0
    
    # Check for balanced braces/brackets (code usually has balanced pairs)
    open_braces = text.count('{')
    close_braces = text.count('}')
    open_parens = text.count('(')
    close_parens = text.count(')')
    
    brace_balance = 1.0 if abs(open_braces - close_braces) <= 1 and open_braces > 0 else 0
    paren_balance = 1.0 if abs(open_parens - close_parens) <= 2 and open_parens > 0 else 0
    scores['balanced_pairs'] = ((brace_balance + paren_balance) / 2) * 0.1
    
    # Penalty for non-code patterns (prose text indicators)
    non_code_matches = count_pattern_matches(text, NON_CODE_PATTERNS)
    # Prose Keywords penalty
    prose_kw_matches = count_pattern_matches(text, PROSE_KEYWORDS)
    
    # Calculate prose ratio
    prose_penalty = (non_code_matches * 0.1) + (prose_kw_matches * 0.02)
    scores['penalty'] = -min(prose_penalty, 0.4)
    
    # Character complexity/density check
    # Code usually has higher density of non-alphanumeric characters
    special_chars = len(re.findall(r'[^a-zA-Z0-9\s]', text))
    density = special_chars / total_chars if total_chars > 0 else 0
    if density > 0.15: # High symbol density is likely code
        scores['density'] = min((density - 0.15) * 0.5, 0.15)
    else:
        scores['density'] = 0.0

    # Calculate overall score
    overall_score = sum(scores.values())
    overall_score = max(0.0, min(1.0, overall_score))
    
    return overall_score, scores


def is_code(text: str, threshold: float = 0.6) -> Tuple[bool, float]:
    """
    Determine if the text content is programming code.
    
    Args:
        text: The text to analyze
        threshold: Minimum score to consider as code (0.6 = 60%)
    
    Returns:
        Tuple of (is_code, confidence_score)
    """
    score, _ = calculate_code_score(text)
    return score >= threshold, score


def detect_primary_language(text: str) -> str:
    """
    Detect the primary programming language of the code.
    
    Returns:
        Language name (e.g., 'python', 'javascript', etc.)
    """
    if not text or not text.strip():
        return 'text'
    
    lang_scores = {}
    
    # Check each language's patterns
    for lang in ['python', 'javascript', 'java', 'c_cpp', 'html', 'css', 'sql', 'shell']:
        if lang in CODE_PATTERNS:
            matches = count_pattern_matches(text, CODE_PATTERNS[lang])
            lang_scores[lang] = matches
    
    # Also check general code patterns for baseline
    keyword_matches = count_pattern_matches(text, CODE_PATTERNS['keywords'])
    
    if not lang_scores or max(lang_scores.values()) == 0:
        if keyword_matches > 0:
            return 'python'  # Default to python for generic code
        return 'text'
    
    # Map c_cpp back to appropriate language
    best_lang = max(lang_scores, key=lang_scores.get)
    if best_lang == 'c_cpp':
        if 'cout' in text or 'cin' in text or 'std::' in text or '::' in text:
            return 'cpp'
        return 'c'
    
    return best_lang


def extract_code_from_text(text: str, min_threshold: float = 0.6) -> Tuple[str, str, float]:
    """
    Extract code content from text, validating it's actually code.
    
    Args:
        text: The text content
        min_threshold: Minimum code confidence threshold (0.6 = 60%)
    
    Returns:
        Tuple of (code_content, detected_language, confidence_score)
        If not code, returns ('', 'text', score)
    """
    if not text or not text.strip():
        return '', 'text', 0.0
    
    text = text.strip()
    
    # Calculate code score
    score, _ = calculate_code_score(text)
    
    if score >= min_threshold:
        language = detect_primary_language(text)
        return text, language, score
    else:
        return '', 'text', score


# Quick test function
if __name__ == "__main__":
    test_cases = [
        # Should be detected as code
        ("def hello():\n    print('Hello World')", True),
        ("function test() { console.log('test'); }", True),
        ("public class Main { public static void main(String[] args) {} }", True),
        ("#include <stdio.h>\nint main() { printf(\"Hi\"); return 0; }", True),
        ("SELECT * FROM users WHERE id = 1;", True),
        ("<html><body><h1>Title</h1></body></html>", True),
        
        # Should NOT be detected as code
        ("Hello, this is a normal sentence.", False),
        ("Dear John, I hope you are doing well.", False),
        ("Meeting notes from today's discussion.", False),
        ("Shopping list: milk, eggs, bread", False),
    ]
    
    print("Code Detection Test Results:")
    print("=" * 60)
    
    for text, expected_is_code in test_cases:
        detected, score = is_code(text)
        status = "[PASS]" if detected == expected_is_code else "[FAIL]"
        print(f"{status} Score: {score:.2f} | Expected: {'Code' if expected_is_code else 'Text'} | Input: {text[:50]}...")
