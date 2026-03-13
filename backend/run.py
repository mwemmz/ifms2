import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Starting IFMS Server...")
    print("="*50)
    
    # Print all registered routes
    print("\n📋 Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"   {rule.methods} {rule}")
    
    port = int(os.environ.get("PORT", 5000))
    print(f"\n✅ Server running at: http://0.0.0.0:{port}")
    print("="*50 + "\n")
    app.run(debug=True, host="0.0.0.0", port=port)