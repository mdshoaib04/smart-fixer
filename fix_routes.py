
import os

def fix_routes():
    routes_path = 'routes.py'
    tracking_path = 'temp_exec/tracking_routes.py'
    
    with open(routes_path, 'rb') as f:
        content = f.read()
        
    # Find the end of valid content (before the appended corrupted part)
    # The last valid part ends with: return jsonify({'days': []}), 500
    marker = b"return jsonify({'days': []}), 500"
    idx = content.rfind(marker)
    
    if idx == -1:
        print("Could not find marker in routes.py")
        return
        
    # Truncate after the marker
    new_content = content[:idx + len(marker)]
    
    # Read the text to append
    with open(tracking_path, 'r', encoding='utf-8') as f:
        append_text = f.read()
        
    # Append
    # Ensure newline
    new_content += b"\n\n" + append_text.encode('utf-8')
    
    with open(routes_path, 'wb') as f:
        f.write(new_content)
        
    print("Fixed routes.py")

if __name__ == "__main__":
    fix_routes()
