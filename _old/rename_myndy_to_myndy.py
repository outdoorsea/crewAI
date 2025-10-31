#!/usr/bin/env python3
"""
Script to rename all instances of "myndy" to "myndy" throughout the crewAI project.
This includes file names, directory names, and content within files.
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple

def find_files_with_memex_content(root_dir: Path) -> List[Path]:
    """Find all files containing 'myndy' in their content."""
    files_with_memex = []
    
    # File extensions to check
    text_extensions = {'.py', '.md', '.txt', '.json', '.yaml', '.yml', '.log', '.toml'}
    
    for file_path in root_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix in text_extensions:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'myndy' in content.lower():
                        files_with_memex.append(file_path)
            except (UnicodeDecodeError, PermissionError):
                # Skip binary files or files we can't read
                continue
    
    return files_with_memex

def find_files_with_memex_names(root_dir: Path) -> List[Path]:
    """Find all files and directories with 'myndy' in their names."""
    items_with_memex = []
    
    for item_path in root_dir.rglob('*'):
        if 'myndy' in item_path.name.lower():
            items_with_memex.append(item_path)
    
    return items_with_memex

def replace_memex_in_content(file_path: Path) -> int:
    """Replace all instances of myndy with myndy in file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count replacements made
        replacements = 0
        
        # Replace different cases of myndy
        patterns = [
            (r'\bMemex\b', 'Myndy'),  # Capitalized
            (r'\bMEMEX\b', 'MYNDY'),  # All caps
            (r'\bmemex\b', 'myndy'),  # Lowercase
        ]
        
        for pattern, replacement in patterns:
            new_content, count = re.subn(pattern, replacement, content)
            content = new_content
            replacements += count
        
        # Write back if changes were made
        if replacements > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Replaced {replacements} instances in {file_path}")
        
        return replacements
        
    except Exception as e:
        print(f"  ✗ Error processing {file_path}: {e}")
        return 0

def rename_file_or_dir(item_path: Path) -> Path:
    """Rename a file or directory by replacing myndy with myndy."""
    old_name = item_path.name
    new_name = old_name.replace('myndy', 'myndy').replace('Myndy', 'Myndy').replace('MYNDY', 'MYNDY')
    
    if new_name != old_name:
        new_path = item_path.parent / new_name
        try:
            item_path.rename(new_path)
            print(f"  ✓ Renamed: {old_name} → {new_name}")
            return new_path
        except Exception as e:
            print(f"  ✗ Error renaming {old_name}: {e}")
            return item_path
    
    return item_path

def main():
    """Main function to perform the myndy to myndy rename operation."""
    print("🔄 Starting myndy → myndy rename operation...")
    print("=" * 50)
    
    # Get the project root (current directory)
    project_root = Path.cwd()
    print(f"Project root: {project_root}")
    
    # Skip certain directories
    skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
    
    # Step 1: Find all files with myndy content
    print("\n📄 Finding files with myndy content...")
    files_with_content = find_files_with_memex_content(project_root)
    print(f"Found {len(files_with_content)} files with myndy content")
    
    # Step 2: Replace content in files
    print("\n🔧 Replacing myndy with myndy in file contents...")
    total_replacements = 0
    
    for file_path in files_with_content:
        # Skip files in ignored directories
        if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
            continue
            
        replacements = replace_memex_in_content(file_path)
        total_replacements += replacements
    
    print(f"✅ Total content replacements: {total_replacements}")
    
    # Step 3: Find files and directories with myndy names
    print("\n📁 Finding files/directories with myndy names...")
    items_with_names = find_files_with_memex_names(project_root)
    # Filter out items in skip directories
    items_with_names = [
        item for item in items_with_names 
        if not any(skip_dir in item.parts for skip_dir in skip_dirs)
    ]
    print(f"Found {len(items_with_names)} items with myndy names")
    
    # Step 4: Rename files and directories (files first, then directories)
    print("\n🏷️  Renaming files and directories...")
    
    # Sort by depth (deepest first) to avoid issues with renaming parent directories
    items_with_names.sort(key=lambda p: len(p.parts), reverse=True)
    
    renamed_count = 0
    for item_path in items_with_names:
        old_name = item_path.name
        new_path = rename_file_or_dir(item_path)
        if new_path.name != old_name:
            renamed_count += 1
    
    print(f"✅ Total items renamed: {renamed_count}")
    
    # Step 5: Summary
    print("\n" + "=" * 50)
    print("🎉 Rename operation completed!")
    print(f"📝 Content replacements: {total_replacements}")
    print(f"📁 Items renamed: {renamed_count}")
    print("\n💡 Next steps:")
    print("   1. Review the changes with 'git diff'")
    print("   2. Test the application to ensure everything works")
    print("   3. Update any remaining hard-coded paths if needed")
    print("   4. Update documentation and README files")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()