import subprocess
import sys
import os
import signal

def signal_handler(sig, frame):
    print("\n👋 Server stopped gracefully.")
    sys.exit(0)

def main():
    print("🚀 Starting SmartFixer Application...")
    print("=" * 50)
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if a port was specified as command line argument
    port = "5000"  # Default port
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    # Run app.py with port argument directly using system Python
    app_py = os.path.join(script_dir, "app.py")
    
    if not os.path.exists(app_py):
        print("❌ app.py not found!")
        return
    
    print("🔧 Launching application...")
    print(f"🌐 URL: http://localhost:{port}")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Run the application with port argument using system Python
        subprocess.run([sys.executable, app_py, "--port", port])
    except KeyboardInterrupt:
        print("\n👋 Application stopped.")
    except Exception as e:
        print(f"❌ Error running application: {e}")

if __name__ == "__main__":
    main()