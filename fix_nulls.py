
import os

def clean_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        if b'\x00' in content:
            print(f"Found null bytes in {filepath}. Cleaning...")
            new_content = content.replace(b'\x00', b'')
            with open(filepath, 'wb') as f:
                f.write(new_content)
            print("File cleaned successfully.")
        else:
            print(f"No null bytes found in {filepath}.")
            
    except Exception as e:
        print(f"Error cleaning file: {e}")

if __name__ == "__main__":
    clean_file('routes.py')
