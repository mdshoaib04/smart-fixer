#!/usr/bin/env python3
from routes import is_programming_code

# Test cases that should be ACCEPTED (valid code)
accepted_tests = [
    ("Python function", "def hello():\n    print('Hello')"),
    ("JavaScript function", "function greet() {\n    console.log('Hello');\n}"),
    ("Java class", "public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println(\"Hello\");\n    }\n}"),
    ("HTML page", "<!DOCTYPE html>\n<html>\n<head>\n    <title>Hello</title>\n</head>\n<body>\n    <div>Hello World</div>\n</body>\n</html>"),
    ("CSS styling", ".container {\n    display: flex;\n    background-color: #f0f0f0;\n}"),
]

# Test cases that should be REJECTED (not code)
rejected_tests = [
    ("Normal text", "This is just normal text with no programming code whatsoever"),
    ("Human faces description", "The image shows a group of people smiling and laughing together"),
    ("Nature scene", "A beautiful landscape with mountains, rivers, and green forests"),
    ("Random text", "Monday Tuesday Wednesday Thursday Friday Saturday Sunday"),
    ("Instructions", "Please read the instructions carefully before proceeding with the next steps"),
]

print("Testing enhanced validation logic...")
print("=" * 50)

all_passed = True

# Test accepted cases
print("Testing cases that SHOULD be accepted (valid code):")
for name, text in accepted_tests:
    result = is_programming_code(text)
    status = "✓ PASS" if result else "✗ FAIL"
    if not result:
        all_passed = False
    print(f"  {status}: {name}")

print("\nTesting cases that SHOULD be rejected (not code):")
for name, text in rejected_tests:
    result = is_programming_code(text)
    status = "✓ PASS" if not result else "✗ FAIL"
    if result:
        all_passed = False
    print(f"  {status}: {name}")

print("\n" + "=" * 50)
if all_passed:
    print("✓ ALL TESTS PASSED! Enhanced validation is working correctly.")
else:
    print("✗ Some tests failed. Check the implementation.")