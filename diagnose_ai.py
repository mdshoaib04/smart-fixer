import os
import multiprocessing
from gpt4all import GPT4All

def diagnose_ai():
    model_name = "Phi-3-mini-4k-instruct.Q4_0.gguf"
    print(f"Diagnosing GPT4All for model: {model_name}")
    
    # Check CPU cores
    cores = multiprocessing.cpu_count()
    print(f"Available CPU logical cores: {cores}")
    
    try:
        # Initialize client
        client = GPT4All(model_name)
        
        # Check current implementation details
        # In newer versions, we can list available models/devices
        print(f"Model loaded: {client.model.model_name}")
        
        # Test a very short generation to see speed
        import time
        start = time.time()
        with client.chat_session():
            response = client.generate("print 'hi'", max_tokens=10)
        end = time.time()
        print(f"Short generation took: {end - start:.2f}s")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error during diagnosis: {e}")

if __name__ == "__main__":
    diagnose_ai()
