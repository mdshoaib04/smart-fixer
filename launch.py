import subprocess
import sys
import os

def main():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if a port was specified as command line argument
    port = "5000"  # Default port
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    # Path to the virtual environment
    venv_path = os.path.join(script_dir, "venv")
    
    # Check if virtual environment exists
    if not os.path.exists(venv_path):
        print("❌ Virtual environment not found!")
        print("Please run the setup first.")
        return
    
    # Path to Python executable in virtual environment
    if sys.platform == "win32":
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_exe = os.path.join(venv_path, "bin", "python")
    
    # Check if Python executable exists
    if not os.path.exists(python_exe):
        print("❌ Python executable not found in virtual environment!")
        return
    
    # Run app.py directly with port argument
    app_py = os.path.join(script_dir, "app.py")
    
    if not os.path.exists(app_py):
        print("❌ app.py not found!")
        return
    
    try:
        # Run the application with port argument
        subprocess.run([python_exe, app_py, "--port", port])
    except KeyboardInterrupt:
        print("\n👋 Application stopped.")
    except Exception as e:
        print(f"❌ Error running application: {e}")

if __name__ == "__main__":
    main()