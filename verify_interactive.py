import socketio
import time
import sys

# Initialize SocketIO client
sio = socketio.Client()

session_id = None
output_received = False

@sio.event
def connect():
    print("Connected to server")

@sio.event
def disconnect():
    print("Disconnected from server")

@sio.on('execution_output')
def on_output(data):
    global output_received
    print(f"Output received: {data['output']}", end='')
    output_received = True
    
    # If prompt detected, send input
    if "Enter name:" in data['output'] or "Enter number:" in data['output']:
        print("\nPrompt detected, sending input...")
        sio.emit('execution_input', {
            'session_id': data['session_id'],
            'input': 'TestUser\n'
        })

@sio.on('execution_finished')
def on_finished(data):
    print(f"\nExecution finished for session {data['session_id']}")
    sio.disconnect()

def test_interactive_execution():
    global session_id
    
    # Connect to the server
    try:
        sio.connect('http://localhost:5000')
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # Python code to test interactivity
    code = """
import time
print("Starting interactive test")
name = input("Enter name: ")
print(f"Hello {name}!")
"""
    
    # Request execution
    print("Requesting execution...")
    # We need to simulate the API call first to get session_id, but the current implementation
    # expects the frontend to generate session_id.
    # So we can just emit execution_input if we knew the session_id, but we need to start it via API.
    
    import requests
    session_id = str(int(time.time()))
    response = requests.post('http://localhost:5000/api/execute', json={
        'code': code,
        'language': 'python',
        'session_id': session_id
    })
    
    print(f"API Response: {response.json()}")
    
    # Wait for execution to complete
    sio.wait()

if __name__ == '__main__':
    test_interactive_execution()
