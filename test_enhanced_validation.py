#!/usr/bin/env python3
"""
Test script for enhanced code validation in OCR and PDF extraction
This script verifies that the system properly distinguishes programming code from normal text
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_enhanced_programming_validation():
    """Test that enhanced programming validation works correctly"""
    
    # Import the validation function we want to test
    from routes import is_programming_code
    
    # Test cases with clear programming code
    programming_texts = [
        # Python
        "def hello_world():\n    print('Hello, World!')\n    return True",
        "class MyClass:\n    def __init__(self):\n        self.value = 0",
        "import os\nfrom typing import List\n\ndef process_files(files: List[str]) -> None:\n    for file in files:\n        print(file)",
        
        # JavaScript
        "function greet(name) {\n    return `Hello, ${name}!`;\n}",
        "const numbers = [1, 2, 3, 4, 5];\nnumbers.forEach(num => console.log(num));",
        "class Rectangle {\n  constructor(width, height) {\n    this.width = width;\n    this.height = height;\n  }\n}",
        
        # Java
        "public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World\");\n    }\n}",
        "import java.util.List;\nimport java.util.ArrayList;\n\npublic class Example {\n    private List<String> items = new ArrayList<>();\n}",
        
        # C++
        "#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << \"Hello, World!\" << endl;\n    return 0;\n}",
        "class Rectangle {\nprivate:\n    int width, height;\npublic:\n    Rectangle(int w, int h) : width(w), height(h) {}\n};",
        
        # HTML/CSS
        "<!DOCTYPE html>\n<html>\n<head>\n    <style>\n        .container { display: flex; }\n    </style>\n</head>\n<body>\n    <div class=\"container\">Hello</div>\n</body>\n</html>",
    ]
    
    # Test cases with normal text (should be rejected)
    normal_texts = [
        "Hello, this is a normal text message with no programming syntax whatsoever.",
        "The quick brown fox jumps over the lazy dog. This is just plain text content.",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt.",
        "This is a sample document with regular text content and no code elements at all.",
        "Monday Tuesday Wednesday Thursday Friday Saturday Sunday January February March",
        "Please read the instructions carefully before proceeding with the next steps.",
        "The weather today is sunny with a high temperature of 75 degrees Fahrenheit.",
        "Contact us at support@example.com for more information about our services."
    ]
    
    # Test cases with mixed content (should be rejected as not primarily code)
    mixed_texts = [
        "Hello everyone, today I'll show you how to write a function.\nJust write some simple code like:\n\nhi there\n\nThat's it!",
        "Please read the instructions carefully before proceeding with the next steps.\nThe weather today is sunny with a high temperature of 75 degrees Fahrenheit.",
        "Contact us at support@example.com for more information about our services.\nMonday Tuesday Wednesday Thursday Friday Saturday Sunday",
        "This is a document about programming.\nIt explains how to write code.\nVery simple stuff.\nEnd of document."
    ]
    
    print("Testing enhanced programming syntax validation...")
    
    # Test that clear programming texts are accepted
    for i, text in enumerate(programming_texts):
        result = is_programming_code(text)
        assert result == True, f"Programming text {i+1} should be detected as code"
        print(f"✓ Programming text {i+1} correctly identified as code")
    
    # Test that normal texts are rejected
    for i, text in enumerate(normal_texts):
        result = is_programming_code(text)
        assert result == False, f"Normal text {i+1} should be rejected as non-code"
        print(f"✓ Normal text {i+1} correctly rejected as non-code")
    
    # Test that mixed texts are rejected (since they're mostly explanatory text)
    for i, text in enumerate(mixed_texts):
        result = is_programming_code(text)
        assert result == False, f"Mixed text {i+1} should be rejected as non-code"
        print(f"✓ Mixed text {i+1} correctly rejected as non-code")
    
    print("\n✓ All enhanced programming syntax validation tests passed!")

def test_edge_cases():
    """Test edge cases for the validation function"""
    
    from routes import is_programming_code
    
    # Test very short text (should be rejected)
    short_text = "hi"
    result = is_programming_code(short_text)
    assert result == False, "Very short text should be rejected"
    print("✓ Very short text correctly rejected")
    
    # Test empty text (should be rejected)
    empty_text = ""
    result = is_programming_code(empty_text)
    assert result == False, "Empty text should be rejected"
    print("✓ Empty text correctly rejected")
    
    # Test text with only code elements but no structure (should be rejected)
    code_elements_only = "{}();=[]{ }"
    result = is_programming_code(code_elements_only)
    assert result == False, "Text with only code elements should be rejected"
    print("✓ Text with only code elements correctly rejected")
    
    print("\n✓ All edge case tests passed!")

if __name__ == "__main__":
    print("Testing enhanced code validation for OCR and PDF extraction...")
    
    try:
        test_enhanced_programming_validation()
        test_edge_cases()
        print("\n✓ All tests passed! Enhanced code validation is working correctly.")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)