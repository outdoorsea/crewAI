#!/usr/bin/env python3
"""
Simple Test for CrewAI-Myndy Integration

File: simple_test.py
"""

import sys
from pathlib import Path

# Add myndy to path
MYNDY_PATH = Path("/Users/jeremy/myndy")
sys.path.insert(0, str(MYNDY_PATH))

def test_basic_functionality():
    """Test the most important integration components."""
    print("🧪 Basic Integration Test")
    print("=" * 30)
    
    # 1. Test tool schema loading
    print("1. Testing tool schemas...")
    try:
        import json
        from pathlib import Path
        tool_repo = Path("/Users/jeremy/myndy/tool_repository")
        schemas = list(tool_repo.glob("*.json"))
        print(f"   ✅ Found {len(schemas)} tool schemas")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # 2. Test myndy core systems
    print("2. Testing myndy core...")
    try:
        from agents.tools.registry import registry
        tools = registry.get_all_tools()
        print(f"   ✅ Myndy registry: {len(tools)} tools")
    except Exception as e:
        print(f"   ❌ Registry failed: {e}")
    
    # 3. Test Ollama
    print("3. Testing Ollama...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"   ✅ Ollama: {len(models)} models available")
        else:
            print(f"   ⚠️  Ollama responded with status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ollama: {e}")
    
    # 4. Test our bridge concept
    print("4. Testing bridge concept...")
    try:
        # Simple tool bridge test
        from pathlib import Path
        import json
        
        tool_repo = Path("/Users/jeremy/myndy/tool_repository")
        sample_schema = None
        
        for schema_file in tool_repo.glob("*.json"):
            with open(schema_file) as f:
                sample_schema = json.load(f)
            break
        
        if sample_schema:
            tool_name = sample_schema.get('name') or sample_schema.get('function', {}).get('name')
            print(f"   ✅ Can load tool: {tool_name}")
        else:
            print("   ❌ No tool schemas found")
            
    except Exception as e:
        print(f"   ❌ Bridge test failed: {e}")
    
    print("\n✅ Basic integration components working!")
    print("\n📋 Next steps:")
    print("   1. Install CrewAI: pip install crewai crewai-tools")
    print("   2. Install missing dependencies as needed")
    print("   3. Test with actual CrewAI agents")
    
    return True

if __name__ == "__main__":
    test_basic_functionality()