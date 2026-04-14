"""
Quick start script for TripVerse backend.
Run this after installing dependencies to set up the backend.
"""

import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file from template."""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return
    
    if env_example.exists():
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✓ Created .env file from template")
        print("  → Edit .env and add your API keys")
    else:
        print("✗ .env.example not found")


def check_dependencies():
    """Check if main dependencies are installed."""
    required = ["fastapi", "langchain", "langgraph", "pydantic", "httpx"]
    missing = []
    
    for package in required:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"✗ Missing packages: {', '.join(missing)}")
        print("  → Run: pip install -r requirements.txt")
        return False
    
    print("✓ All dependencies installed")
    return True


def test_imports():
    """Test if core modules can be imported."""
    try:
        import config
        import llm_client
        import vector_db
        import orchestrator
        print("✓ Core modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*50)
    print("TripVerse Backend Setup Complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Edit .env file with your API keys:")
    print("   - OpenAI API Key (or Anthropic)")
    print("   - Pinecone API Key (or other vector DB)")
    print("\n2. Start the server:")
    print("   python main.py")
    print("\n3. Visit API documentation:")
    print("   http://localhost:8000/docs")
    print("\n4. Make your first request:")
    print("   curl -X POST http://localhost:8000/api/trips/plan \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print('       \"trip_description\": \"7 days in Japan\",')
    print('       \"budget\": \"Balanced\",')
    print('       \"pace\": \"Balanced\",')
    print('       \"starting_from\": \"New York\"')
    print("     }'")
    print("="*50 + "\n")


def main():
    """Run setup checks."""
    print("\nTripVerse Backend Setup\n")
    
    create_env_file()
    
    if not check_dependencies():
        return
    
    if not test_imports():
        print("⚠️  Some modules have issues, but you can still try running the server")
    
    print_next_steps()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)
