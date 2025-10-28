from routes import is_programming_code

# Test cases
test_cases = [
    ("Python function", "def hello():\n    print('Hello')"),
    ("JavaScript function", "function greet() {\n    console.log('Hello');\n}"),
    ("Simple HTML", "<html><body><div>Hello</div></body></html>"),
    ("Normal text", "This is just normal text with no code"),
]

for name, text in test_cases:
    result = is_programming_code(text)
    print(f"{name}: {result}")