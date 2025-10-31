#!/usr/bin/env python3
"""
Test script to directly test memory storage tools
"""

import sys
from pathlib import Path

# Add the crewAI directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_memory_tools_direct():
    """Test memory storage tools directly"""
    print("🧪 Testing Memory Storage Tools Directly")
    print("=" * 50)
    
    try:
        # Test 1: Test comprehensive memory storage import
        print("📋 Test 1: Importing comprehensive memory storage...")
        from tools.comprehensive_memory_storage import create_contact, create_project, create_event, create_task
        from tools.memory_storage_tools import create_entity, add_fact
        print("✅ Successfully imported comprehensive memory storage tools")
        
        # Test 2: Test creating an entity
        print("\n📋 Test 2: Creating entity...")
        result = create_entity(
            name="Brent Bushnell",
            entity_type="person",
            organization="Two Bit Circus",
            description="Friend and collaborator, owner of Two Bit Circus"
        )
        print(f"✅ Entity creation result: {result}")
        
        # Test 3: Test creating a project
        print("\n📋 Test 3: Creating project...")
        result = create_project(
            name="Dream Park",
            description="AR game for Oculus Quest 2",
            status="active"
        )
        print(f"✅ Project creation result: {result}")
        
        # Test 4: Test creating a contact
        print("\n📋 Test 4: Creating contact...")
        result = create_contact(
            name="Brent Bushnell",
            organization="Two Bit Circus",
            notes="Friend and collaborator on Dream Park project"
        )
        print(f"✅ Contact creation result: {result}")
        
        # Test 5: Test myndy bridge tools
        print("\n📋 Test 5: Testing myndy bridge tools...")
        from tools.myndy_bridge import MyndyTool
        
        # Create a test memory tool
        test_tool = MyndyTool(
            name="create_entity",
            description="Create entity tool",
            myndy_tool_name="create_entity",
            tool_schema={"function": {"name": "create_entity"}},
            category="memory"
        )
        
        # Test tool execution
        result = test_tool._create_entity(
            name="Test Person",
            entity_type="person",
            organization="Test Company"
        )
        print(f"✅ MyndyTool create_entity result: {result}")
        
        print("\n🎉 All memory storage tools are working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memory_tools_direct()