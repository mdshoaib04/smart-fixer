#!/usr/bin/env python3
from routes import is_programming_code

# Test the problematic HTML case
text = '''<!DOCTYPE html>
<html>
<head>
    <style>
        .container { display: flex; }
    </style>
</head>
<body>
    <div class="container">Hello</div>
</body>
</html>'''

print("Testing HTML/CSS example:")
print("Text:", repr(text))
result = is_programming_code(text)
print("Result:", result)

# Test a simpler HTML case
simple_html = "<html><body><div>Hello</div></body></html>"
print("\nTesting simple HTML:")
print("Text:", repr(simple_html))
result = is_programming_code(simple_html)
print("Result:", result)