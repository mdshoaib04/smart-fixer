#!/usr/bin/env python3
"""
Setup script for SmartFixer
This script helps install all required dependencies for the SmartFixer application.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages from requirements.txt"""
    try:
        # Check if requirements.txt exists
        if not os.path.exists('requirements.txt'):
            print("❌ requirements.txt not found!")
            return False
            
        print("📦 Installing required packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ All required packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    except FileNotFoundError:
        print("❌ pip not found. Please make sure Python and pip are installed.")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python 3.7+ is required. You have Python {version.major}.{version.minor}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def main():
    print("🚀 SmartFixer Setup")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install requirements
    if install_requirements():
        print("\n🎉 Setup completed successfully!")
        print("\nTo run SmartFixer:")
        print("  python app.py")
        print("  # or")
        print("  python main.py")
        print("\nThen open your browser to http://localhost:5000")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()