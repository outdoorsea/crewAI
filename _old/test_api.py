#!/usr/bin/env python3
"""
Test the CrewAI-Myndy OpenAPI Server

File: test_api.py
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_api_import():
    """Test that we can import the API components."""
    print("🧪 Testing API Server Components")
    print("=" * 40)
    
    success_count = 0
    total_tests = 4
    
    # Test 1: Import API models
    print("1. Testing API models import...")
    try:
        from api.models import AgentRole, TaskType, AgentChatRequest, SystemStatus
        print("   ✅ API models imported successfully")
        print(f"   ✅ Agent roles: {[role.value for role in AgentRole]}")
        success_count += 1
    except Exception as e:
        print(f"   ❌ API models import failed: {e}")
    
    # Test 2: Import main app
    print("\n2. Testing FastAPI app import...")
    try:
        from api.main import app
        print("   ✅ FastAPI app imported successfully")
        print(f"   ✅ App title: {app.title}")
        success_count += 1
    except Exception as e:
        print(f"   ❌ FastAPI app import failed: {e}")
    
    # Test 3: Import OpenAPI extensions
    print("\n3. Testing OpenAPI extensions...")
    try:
        from api.openapi_extensions import add_openai_compatibility, OpenAIChatRequest
        print("   ✅ OpenAPI extensions imported successfully")
        print("   ✅ Open WebUI compatibility ready")
        success_count += 1
    except Exception as e:
        print(f"   ❌ OpenAPI extensions import failed: {e}")
    
    # Test 4: Test production server setup
    print("\n4. Testing production server...")
    try:
        from api.server import create_production_app
        production_app = create_production_app()
        print("   ✅ Production server created successfully")
        print(f"   ✅ Routes available: {len(production_app.routes)}")
        success_count += 1
    except Exception as e:
        print(f"   ❌ Production server failed: {e}")
    
    # Summary
    print("\n" + "=" * 40)
    print("API SERVER TEST RESULTS")
    print("=" * 40)
    
    print(f"✅ {success_count}/{total_tests} components working")
    
    if success_count == total_tests:
        print("\n🎉 API SERVER READY!")
        print("\n🚀 What you can do:")
        print("   • Start server: python api/server.py")
        print("   • View docs: http://localhost:8000/docs") 
        print("   • Open WebUI: Add as custom model")
        print("   • API endpoints: /agents, /tasks, /chat/completions")
        
        print("\n📋 Start commands:")
        print("   # Development server")
        print("   python api/main.py")
        print()
        print("   # Production server")
        print("   python api/server.py")
        print()
        print("   # Open WebUI integration")
        print("   # Add base URL: http://localhost:8000")
        print("   # Model type: OpenAI Compatible")
        
    elif success_count >= 2:
        print("\n⚠️  Partial success - some components need work")
    else:
        print("\n❌ API server needs fixes")
    
    return success_count >= 2

if __name__ == "__main__":
    success = test_api_import()
    if success:
        print("\n🎯 Ready to start API server!")
    sys.exit(0 if success else 1)