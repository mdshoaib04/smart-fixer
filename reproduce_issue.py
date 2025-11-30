
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from ai_models import review_code, explain_code, detect_language

java_code = """
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
"""

print("Testing Language Detection...")
detected = detect_language(java_code)
print(f"Detected Language: {detected}")

print("\nTesting Review Code (Java)...")
review = review_code(java_code, "java")
print(f"Review Result: {review}")

print("\nTesting Explain Code (Java)...")
explanation = explain_code(java_code, "java")
print(f"Explanation Result: {explanation}")
