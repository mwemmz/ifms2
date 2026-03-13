import sys
print(f"Python path: {sys.executable}")

# These imports should work even if Pylance shows errors
try:
    from flask import Flask
    print("✓ Flask imported")
except ImportError as e:
    print(f"✗ Flask failed: {e}")

try:
    from flask_sqlalchemy import SQLAlchemy
    print("✓ SQLAlchemy imported")
except ImportError as e:
    print(f"✗ SQLAlchemy failed: {e}")

print("\nIf you see ✓ marks above, your code will run even though Pylance shows errors.")