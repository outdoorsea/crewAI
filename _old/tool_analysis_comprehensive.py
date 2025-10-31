#!/usr/bin/env python3
"""
Comprehensive Tool Analysis Script
Analyzes missing tools in the Myndy bridge and role mappings
"""

import json
import os
from pathlib import Path

def analyze_tool_availability():
    """Analyze tool availability vs. requests"""
    
    # 1. Get tools from repository
    repo_path = Path("/Users/jeremy/myndy-ai/tool_repository")
    repo_tools = set()
    
    if repo_path.exists():
        for json_file in repo_path.glob("*.json"):
            tool_name = json_file.stem
            repo_tools.add(tool_name)
    
    print(f"🗂️  Tools in repository: {len(repo_tools)}")
    print(f"Repository tools: {sorted(repo_tools)}")
    print()
    
    # 2. Get tools from role mappings in myndy_bridge.py
    role_tool_mappings = {
        "context_manager": [
            "get_current_time",
            "format_date"
        ],
        "memory_librarian": [
            "extract_conversation_entities",
            "search_conversation_memory", 
            "get_conversation_summary"
        ],
        "personal_assistant": [
            "get_current_time",
            "local_weather",
            "format_weather", 
            "weather_api",
            "format_date",
            "calculate_time_difference"
        ],
        "research_specialist": [
            "analyze_text",
            "analyze_sentiment",
            "summarize_text",
            "detect_language"
        ],
        "health_analyst": [
            "health_query_simple",
            "health_summary_simple"
        ],
        "finance_tracker": [
            "finance_tool"
        ]
    }
    
    all_mapped_tools = set()
    for role, tools in role_tool_mappings.items():
        all_mapped_tools.update(tools)
    
    print(f"🎯 Tools in role mappings: {len(all_mapped_tools)}")
    print(f"Mapped tools: {sorted(all_mapped_tools)}")
    print()
    
    # 3. Find missing tools (in mappings but not in repo)
    missing_tools = all_mapped_tools - repo_tools
    print(f"❌ Missing tools (in mappings but not in repo): {len(missing_tools)}")
    for tool in sorted(missing_tools):
        print(f"   - {tool}")
    print()
    
    # 4. Find available tools not used in mappings
    unused_tools = repo_tools - all_mapped_tools
    print(f"💡 Available tools not used in mappings: {len(unused_tools)}")
    for tool in sorted(unused_tools):
        print(f"   - {tool}")
    print()
    
    # 5. Check built-in implementations in myndy_bridge.py
    built_in_tools = [
        "get_current_time",
        "format_weather",
        "local_weather",
        "weather_api"
    ]
    
    print(f"🔧 Built-in tool implementations: {len(built_in_tools)}")
    for tool in built_in_tools:
        print(f"   - {tool}")
    print()
    
    # 6. Analyze by role
    print("📋 Tool analysis by role:")
    print("=" * 50)
    
    for role, tools in role_tool_mappings.items():
        print(f"\n🤖 {role}:")
        print(f"   Requested tools: {len(tools)}")
        
        available = []
        missing = []
        
        for tool in tools:
            if tool in repo_tools or tool in built_in_tools:
                available.append(tool)
            else:
                missing.append(tool)
        
        print(f"   ✅ Available: {len(available)}")
        for tool in available:
            source = "repo" if tool in repo_tools else "built-in"
            print(f"      - {tool} ({source})")
        
        print(f"   ❌ Missing: {len(missing)}")
        for tool in missing:
            print(f"      - {tool}")
    
    # 7. Recommendations
    print("\n🎯 RECOMMENDATIONS:")
    print("=" * 50)
    
    if missing_tools:
        print("\n1. PRIORITY: Implement missing tools")
        for tool in sorted(missing_tools):
            # Try to suggest what the tool might do based on name
            suggestions = {
                "search_conversation_memory": "Search stored conversations in vector DB",
                "get_conversation_summary": "Get summary of conversation analysis",
                "format_date": "Format date/time strings",
                "calculate_time_difference": "Calculate time differences",
                "health_query_simple": "Simple health data queries"
            }
            suggestion = suggestions.get(tool, "Tool functionality needs to be implemented")
            print(f"   - {tool}: {suggestion}")
    
    if unused_tools:
        print(f"\n2. OPTIMIZATION: Consider using {len(unused_tools)} available tools")
        # Group by category
        categories = {}
        for tool in unused_tools:
            # Categorize by prefix or pattern
            if any(x in tool for x in ['document', 'extract', 'process']):
                cat = 'document_processing'
            elif any(x in tool for x in ['transaction', 'expense', 'spending']):
                cat = 'finance'
            elif any(x in tool for x in ['health']):
                cat = 'health'
            elif any(x in tool for x in ['unix', 'timestamp']):
                cat = 'time'
            else:
                cat = 'general'
            
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(tool)
        
        for cat, tools in categories.items():
            print(f"   {cat}: {', '.join(tools)}")
    
    print(f"\n3. COVERAGE: {len(all_mapped_tools - missing_tools)}/{len(all_mapped_tools)} tools available ({(len(all_mapped_tools - missing_tools)/len(all_mapped_tools)*100):.1f}%)")
    
    return {
        'repo_tools': repo_tools,
        'mapped_tools': all_mapped_tools,
        'missing_tools': missing_tools,
        'unused_tools': unused_tools,
        'built_in_tools': built_in_tools,
        'role_mappings': role_tool_mappings
    }

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE TOOL ANALYSIS")
    print("=" * 60)
    print()
    
    analysis = analyze_tool_availability()
    
    print(f"\n📊 SUMMARY:")
    print(f"   Repository tools: {len(analysis['repo_tools'])}")
    print(f"   Mapped tools: {len(analysis['mapped_tools'])}")
    print(f"   Missing tools: {len(analysis['missing_tools'])}")
    print(f"   Unused tools: {len(analysis['unused_tools'])}")
    print(f"   Built-in tools: {len(analysis['built_in_tools'])}")