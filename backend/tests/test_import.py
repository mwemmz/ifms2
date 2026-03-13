import sys
import os

print("Current directory:", os.getcwd())
print("\nPython path:", sys.path)

try:
    from app import create_app
    print("\n✓ Successfully imported create_app from app")
except Exception as e:
    print(f"\n✗ Error importing: {e}")

# Check if app/__init__.py exists
app_init_path = os.path.join(os.getcwd(), 'app', '__init__.py')
print(f"\napp/__init__.py exists: {os.path.exists(app_init_path)}")

# List contents of app directory
app_dir = os.path.join(os.getcwd(), 'app')
if os.path.exists(app_dir):
    print("\nContents of app directory:")
    for item in os.listdir(app_dir):
        print(f"  - {item}")