#!/usr/bin/env python3
"""
Script to convert all markdown (.md) files from "memex" to "myndy".
This script specifically focuses on markdown files and handles various markdown-specific cases.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

def find_markdown_files(root_dir: Path) -> List[Path]:
    """Find all markdown files in the project."""
    markdown_files = []
    
    # Skip certain directories
    skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv', '.claude'}
    
    for file_path in root_dir.rglob('*.md'):
        # Skip files in ignored directories
        if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
            continue
        markdown_files.append(file_path)
    
    return sorted(markdown_files)

def convert_markdown_content(content: str) -> Tuple[str, int]:
    """Convert memex to myndy in markdown content with special handling for markdown syntax."""
    
    replacements_made = 0
    
    # Define replacement patterns with different cases and contexts
    patterns = [
        # Basic word replacements
        (r'\bMemex\b', 'Myndy'),           # Capitalized
        (r'\bMEMEX\b', 'MYNDY'),           # All caps
        (r'\bmemex\b', 'myndy'),           # Lowercase
        
        # URL and path patterns
        (r'/memex/', '/myndy/'),           # Paths
        (r'=memex', '=myndy'),             # URLs/paths
        (r'memex-', 'myndy-'),             # Hyphenated terms
        (r'memex_', 'myndy_'),             # Underscored terms
        
        # Code block and inline code patterns
        (r'`memex`', '`myndy`'),           # Inline code
        (r'`Memex`', '`Myndy`'),           # Inline code capitalized
        (r'"memex"', '"myndy"'),           # Quoted strings
        (r"'memex'", "'myndy'"),           # Single quoted strings
        
        # Header and title patterns
        (r'# (.*)Memex(.*)', r'# \1Myndy\2'),     # Headers with Memex
        (r'## (.*)Memex(.*)', r'## \1Myndy\2'),   # Subheaders
        (r'### (.*)Memex(.*)', r'### \1Myndy\2'), # Sub-subheaders
        
        # Link patterns [text](url) and [text]: url
        (r'\[([^\]]*)[Mm]emex([^\]]*)\]', r'[\1myndy\2]'),  # Link text
        (r'\(([^)]*)/memex/', r'(\1/myndy/'),               # Link URLs
        
        # Image patterns ![alt](src)
        (r'!\[([^\]]*)[Mm]emex([^\]]*)\]', r'![\1myndy\2]'),
        
        # Table cell content
        (r'\|([^|]*)[Mm]emex([^|]*)\|', r'|\1myndy\2|'),
        
        # List item patterns
        (r'^(\s*[-*+]\s+.*)[Mm]emex(.*)$', r'\1myndy\2', re.MULTILINE),
        (r'^(\s*\d+\.\s+.*)[Mm]emex(.*)$', r'\1myndy\2', re.MULTILINE),
        
        # Configuration and property patterns
        (r'memex_path:', 'myndy_path:'),
        (r'memexPath:', 'myndyPath:'),
        (r'MEMEX_PATH', 'MYNDY_PATH'),
        
        # Docker and container patterns
        (r'crewai-memex', 'crewai-myndy'),
        (r'memex-pipeline', 'myndy-pipeline'),
        
        # Environment variable patterns
        (r'\$\{MEMEX_', '${MYNDY_'),
        (r'\$MEMEX_', '$MYNDY_'),
        
        # JSON/YAML key patterns
        (r'"memex":', '"myndy":'),
        (r'memex:', 'myndy:'),
        
        # Class and module patterns in documentation
        (r'MemexTool', 'MyndyTool'),
        (r'MemexToolLoader', 'MyndyToolLoader'),
        (r'MemexBridge', 'MyndyBridge'),
        (r'memex_bridge', 'myndy_bridge'),
        (r'memex_memory', 'myndy_memory'),
        
        # API endpoint patterns
        (r'/api/memex/', '/api/myndy/'),
        (r'api/memex', 'api/myndy'),
        
        # File extension and format patterns
        (r'\.memex', '.myndy'),
        (r'_memex\.', '_myndy.'),
        (r'-memex\.', '-myndy.'),
    ]
    
    # Apply all patterns
    for pattern, replacement, *flags in patterns:
        flag = flags[0] if flags else 0
        if flag:
            new_content, count = re.subn(pattern, replacement, content, flags=flag)
        else:
            new_content, count = re.subn(pattern, replacement, content)
        content = new_content
        replacements_made += count
    
    return content, replacements_made

def process_markdown_file(file_path: Path) -> Dict[str, any]:
    """Process a single markdown file and convert memex to myndy."""
    result = {
        'file': str(file_path),
        'replacements': 0,
        'success': False,
        'error': None,
        'changes': []
    }
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Convert content
        new_content, replacements = convert_markdown_content(original_content)
        
        # Write back if changes were made
        if replacements > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            result['replacements'] = replacements
            result['success'] = True
            
            # Find specific changes for reporting
            original_lines = original_content.split('\n')
            new_lines = new_content.split('\n')
            
            for i, (old_line, new_line) in enumerate(zip(original_lines, new_lines)):
                if old_line != new_line:
                    result['changes'].append({
                        'line': i + 1,
                        'old': old_line.strip(),
                        'new': new_line.strip()
                    })
        else:
            result['success'] = True
            result['replacements'] = 0
    
    except Exception as e:
        result['error'] = str(e)
    
    return result

def main():
    """Main function to convert all markdown files."""
    print("📝 Converting Markdown Files: memex → myndy")
    print("=" * 50)
    
    # Get project root
    project_root = Path.cwd()
    print(f"Project root: {project_root}")
    
    # Find all markdown files
    print("\n🔍 Finding markdown files...")
    markdown_files = find_markdown_files(project_root)
    print(f"Found {len(markdown_files)} markdown files")
    
    if not markdown_files:
        print("❌ No markdown files found!")
        return
    
    # Process each file
    print("\n🔧 Processing markdown files...")
    total_replacements = 0
    successful_files = 0
    failed_files = 0
    files_with_changes = 0
    
    for file_path in markdown_files:
        print(f"\n📄 Processing: {file_path.name}")
        result = process_markdown_file(file_path)
        
        if result['success']:
            successful_files += 1
            if result['replacements'] > 0:
                files_with_changes += 1
                total_replacements += result['replacements']
                print(f"  ✅ {result['replacements']} replacements made")
                
                # Show first few changes for verification
                if result['changes']:
                    print("  📝 Sample changes:")
                    for change in result['changes'][:3]:  # Show first 3 changes
                        print(f"    Line {change['line']}: {change['old']} → {change['new']}")
                    if len(result['changes']) > 3:
                        print(f"    ... and {len(result['changes']) - 3} more changes")
            else:
                print("  ℹ️  No changes needed")
        else:
            failed_files += 1
            print(f"  ❌ Error: {result['error']}")
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 Markdown Conversion Complete!")
    print(f"📊 Summary:")
    print(f"   📁 Total markdown files: {len(markdown_files)}")
    print(f"   ✅ Successfully processed: {successful_files}")
    print(f"   ❌ Failed: {failed_files}")
    print(f"   📝 Files with changes: {files_with_changes}")
    print(f"   🔄 Total replacements: {total_replacements}")
    
    if files_with_changes > 0:
        print(f"\n💡 Next steps:")
        print(f"   1. Review changes with: git diff *.md")
        print(f"   2. Check that all markdown links still work")
        print(f"   3. Verify that code examples are still correct")
        print(f"   4. Update any remaining hardcoded references")
    
    print(f"\n✨ All markdown files have been converted from memex to myndy!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()