import os
import shutil

# Replicate the logic from routes.py
scoop_path = os.path.expanduser('~/scoop/shims')
if scoop_path not in os.environ['PATH']:
    print(f"Adding Scoop path: {scoop_path}")
    os.environ['PATH'] += os.pathsep + scoop_path
else:
    print("Scoop path already in PATH")

print(f"Current PATH: {os.environ['PATH']}")

# Check for Java
java_path = shutil.which('java')
print(f"Java found at: {java_path}")

# Check for GCC
gcc_path = shutil.which('gcc')
print(f"GCC found at: {gcc_path}")
