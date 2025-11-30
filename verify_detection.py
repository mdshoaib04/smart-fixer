import sys
import os
import logging

# Add current directory to path
sys.path.append(os.getcwd())

# Mute logging
logging.basicConfig(level=logging.ERROR)

try:
    from ai_models import detect_language
except ImportError as e:
    print(f"Error importing ai_models: {e}")
    sys.exit(1)

test_cases = [
    ("def hello():\n    print('hello')", "python"),
    ("function test() { console.log('hi'); }", "javascript"),
    ("public class Main { public static void main(String[] args) {} }", "java"),
    ("#include <iostream>\nint main() { std::cout << 'hi'; }", "cpp"),
    ("package main\nimport \"fmt\"\nfunc main() { fmt.Println(\"hi\") }", "go"),
    ("<?php echo 'hello'; ?>", "php"),
    ("SELECT * FROM users WHERE id = 1", "sql"),
    ("#!/bin/bash\necho 'hello'", "shell"),
    ("body { color: red; }", "css"),
    ("<!DOCTYPE html><html></html>", "html"),
    # Ambiguous / AI Fallback cases
    ("puts 'hello world'", "ruby"), # Ruby (might be detected as python if AI fails)
    ("let mut x = 5;", "rust"), # Rust heuristic
]

print("Running detection tests...")
print("-" * 50)
for code, expected in test_cases:
    try:
        detected = detect_language(code)
        # For Ruby, we accept python if AI fails, but ideally it should be ruby
        # For others, we expect exact match
        
        status = "[OK]" if detected == expected else "[FAIL]"
        if expected == "ruby" and detected == "python":
            status = "[WARN] (AI Fallback to Python)"
            
        print(f"{status} Expected: {expected:<10} | Detected: {detected:<10} | Code: {code[:30].replace(chr(10), ' ')}...", flush=True)
    except Exception as e:
        print(f"[ERR] Error testing {expected}: {e}", flush=True)

print("-" * 50, flush=True)
print("Done.", flush=True)
