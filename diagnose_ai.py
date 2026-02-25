import os
import multiprocessing

try:
    from gpt4all import GPT4All
except Exception:
    GPT4All = None


def diagnose_ai():
    model_name = "Phi-3-mini-4k-instruct.Q4_0.gguf"
    print(f"Diagnosing GPT4All for model: {model_name}")
    
    cores = multiprocessing.cpu_count()
    print(f"Available CPU logical cores: {cores}")
    
    if GPT4All is None:
        print("GPT4All library is not installed. Install it to enable local model diagnostics.")
        return

    try:
        client = GPT4All(model_name)
        print(f"Model loaded: {getattr(getattr(client, 'model', None), 'model_name', 'unknown')}")
        
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
