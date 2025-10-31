#!/usr/bin/env python3
"""
Comprehensive Memex to Myndy Replacement Script

This script performs an extensive search and replace operation to convert all
instances of "memex" to "myndy" throughout the entire codebase, following
proper case sensitivity rules and handling various naming conventions.

Usage: python comprehensive_memex_to_myndy_replacement.py

Author: Claude Code Assistant
Date: January 2025
"""

import os
import re
import shutil
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Set
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('memex_to_myndy_replacement.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveReplacer:
    """Comprehensive memex to myndy replacement handler"""
    
    def __init__(self, project_root: str = "/Users/jeremy/crewAI"):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_before_replacement"
        
        # Statistics tracking
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'files_renamed': 0,
            'total_replacements': 0,
            'replacement_patterns': {},
            'errors': []
        }
        
        # Define all possible case variations and patterns
        self.replacement_patterns = [
            # Direct word replacements (case sensitive)
            (r'\bmemex\b', 'myndy'),           # memex -> myndy
            (r'\bMemex\b', 'Myndy'),           # Memex -> Myndy  
            (r'\bMEMEX\b', 'MYNDY'),           # MEMEX -> MYNDY
            
            # CamelCase patterns
            (r'\bmemexBridge\b', 'myndyBridge'),
            (r'\bMemexBridge\b', 'MyndyBridge'),
            (r'\bmemexTool\b', 'myndyTool'),
            (r'\bMemexTool\b', 'MyndyTool'),
            (r'\bmemexToolLoader\b', 'myndyToolLoader'),
            (r'\bMemexToolLoader\b', 'MyndyToolLoader'),
            (r'\bmemexToolError\b', 'myndyToolError'),
            (r'\bMemexToolError\b', 'MyndyToolError'),
            (r'\bmemexRegistry\b', 'myndyRegistry'),
            (r'\bMemexRegistry\b', 'MyndyRegistry'),
            (r'\bmemexMemory\b', 'myndyMemory'),
            (r'\bMemexMemory\b', 'MyndyMemory'),
            (r'\bmemexIntegration\b', 'myndyIntegration'),
            (r'\bMemexIntegration\b', 'MyndyIntegration'),
            
            # Snake_case patterns  
            (r'\bmemex_bridge\b', 'myndy_bridge'),
            (r'\bmemex_tool\b', 'myndy_tool'),
            (r'\bmemex_tool_loader\b', 'myndy_tool_loader'),
            (r'\bmemex_tool_error\b', 'myndy_tool_error'),
            (r'\bmemex_registry\b', 'myndy_registry'),
            (r'\bmemex_memory\b', 'myndy_memory'),
            (r'\bmemex_integration\b', 'myndy_integration'),
            (r'\bmemex_data\b', 'myndy_data'),
            (r'\bmemex_storage\b', 'myndy_storage'),
            (r'\bmemex_config\b', 'myndy_config'),
            (r'\bmemex_tools\b', 'myndy_tools'),
            (r'\bmemex_api\b', 'myndy_api'),
            (r'\bmemex_server\b', 'myndy_server'),
            (r'\bmemex_pipeline\b', 'myndy_pipeline'),
            (r'\bmemex_client\b', 'myndy_client'),
            
            # Kebab-case patterns
            (r'\bmemex-bridge\b', 'myndy-bridge'),
            (r'\bmemex-tool\b', 'myndy-tool'),
            (r'\bmemex-api\b', 'myndy-api'),
            (r'\bmemex-server\b', 'myndy-server'),
            (r'\bmemex-pipeline\b', 'myndy-pipeline'),
            
            # Function and method patterns
            (r'\bload_memex_tools\b', 'load_myndy_tools'),
            (r'\bload_all_memex_tools\b', 'load_all_myndy_tools'),
            (r'\bload_memex_tools_for_agent\b', 'load_myndy_tools_for_agent'),
            (r'\bget_memex_tool\b', 'get_myndy_tool'),
            (r'\bcreate_memex_bridge\b', 'create_myndy_bridge'),
            (r'\binit_memex_system\b', 'init_myndy_system'),
            (r'\bmemex_tool_registry\b', 'myndy_tool_registry'),
            
            # Class inheritance and type patterns
            (r'\bMemoryAwareAgent\b', 'MyndyAwareAgent'),
            (r'\bCrewAIMemoryBridge\b', 'CrewAIMyndyBridge'),
            (r'\bMemexMemoryIntegration\b', 'MyndyMemoryIntegration'),
            
            # Import patterns
            (r'from\s+tools\.memex_bridge\b', 'from tools.myndy_bridge'),
            (r'import\s+memex_bridge\b', 'import myndy_bridge'),
            (r'from\s+memory\.memex_memory_integration\b', 'from memory.myndy_memory_integration'),
            (r'import\s+memex_memory_integration\b', 'import myndy_memory_integration'),
            
            # File path patterns
            (r'/memex_bridge\.py\b', '/myndy_bridge.py'),
            (r'/memex_memory_integration\.py\b', '/myndy_memory_integration.py'),
            (r'/memex_data/', '/myndy_data/'),
            (r'/memex/', '/myndy/'),
            
            # URL and endpoint patterns
            (r'/api/memex\b', '/api/myndy'),
            (r'/memex/api\b', '/myndy/api'),
            
            # Environment variable patterns
            (r'\bMEMEX_API_KEY\b', 'MYNDY_API_KEY'),
            (r'\bMEMEX_PATH\b', 'MYNDY_PATH'),
            (r'\bMEMEX_CONFIG\b', 'MYNDY_CONFIG'),
            (r'\bMEMEX_URL\b', 'MYNDY_URL'),
            
            # Configuration patterns
            (r'"memex_path"', '"myndy_path"'),
            (r"'memex_path'", "'myndy_path'"),
            (r'"memex_api"', '"myndy_api"'),
            (r"'memex_api'", "'myndy_api'"),
            
            # Comment patterns
            (r'# Memex\b', '# Myndy'),
            (r'# memex\b', '# myndy'),
            (r'## Memex\b', '## Myndy'),
            (r'## memex\b', '## myndy'),
            (r'### Memex\b', '### Myndy'),
            (r'### memex\b', '### myndy'),
            (r'"""Memex\b', '"""Myndy'),
            (r'"""memex\b', '"""myndy'),
            
            # Documentation patterns
            (r'Memex AI\b', 'Myndy AI'),
            (r'memex ai\b', 'myndy ai'),
            (r'MEMEX AI\b', 'MYNDY AI'),
            (r'Memex System\b', 'Myndy System'),
            (r'memex system\b', 'myndy system'),
            (r'Memex Tool\b', 'Myndy Tool'),
            (r'memex tool\b', 'myndy tool'),
            (r'Memex Bridge\b', 'Myndy Bridge'),
            (r'memex bridge\b', 'myndy bridge'),
            
            # Logging and error messages
            (r'Loading Memex\b', 'Loading Myndy'),
            (r'loading memex\b', 'loading myndy'),
            (r'Memex loaded\b', 'Myndy loaded'),
            (r'memex loaded\b', 'myndy loaded'),
            (r'Memex error\b', 'Myndy error'),
            (r'memex error\b', 'myndy error'),
            
            # Version and metadata patterns
            (r'memex-v', 'myndy-v'),
            (r'memex_v', 'myndy_v'),
            (r'memex-version', 'myndy-version'),
            (r'memex_version', 'myndy_version'),
        ]
        
        # File extensions to process
        self.file_extensions = {
            '.py', '.md', '.txt', '.json', '.yaml', '.yml', 
            '.toml', '.cfg', '.ini', '.log', '.sh', '.bash',
            '.js', '.ts', '.html', '.css', '.sql', '.env'
        }
        
        # Directories to skip
        self.skip_directories = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.venv', 'venv', 'env', '.env', 'backup_before_replacement',
            '.claude', 'build', 'dist', '.mypy_cache'
        }
        
        # Files to skip
        self.skip_files = {
            'comprehensive_memex_to_myndy_replacement.py',
            'memex_to_myndy_replacement.log',
            'rename_memex_to_myndy.py',
            'convert_md_memex_to_myndy.py'
        }

    def create_backup(self):
        """Create a backup of the entire project before making changes"""
        logger.info("Creating backup...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # Copy entire project (excluding certain directories)
        self.backup_dir.mkdir(parents=True)
        
        for item in self.project_root.iterdir():
            if item.name not in self.skip_directories and item != self.backup_dir:
                if item.is_file():
                    shutil.copy2(item, self.backup_dir)
                elif item.is_dir():
                    shutil.copytree(item, self.backup_dir / item.name, 
                                  ignore=shutil.ignore_patterns(*self.skip_directories))
        
        logger.info(f"Backup created at: {self.backup_dir}")

    def find_files_to_process(self) -> List[Path]:
        """Find all files that should be processed"""
        files_to_process = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in self.skip_directories]
            
            root_path = Path(root)
            
            # Skip backup directory
            if self.backup_dir in root_path.parents or root_path == self.backup_dir:
                continue
            
            for file in files:
                file_path = root_path / file
                
                # Skip certain files
                if file in self.skip_files:
                    continue
                
                # Process files with relevant extensions or files containing 'memex'
                if (file_path.suffix.lower() in self.file_extensions or 
                    'memex' in file.lower()):
                    files_to_process.append(file_path)
        
        return files_to_process

    def process_file_content(self, file_path: Path) -> Tuple[str, int]:
        """Process file content and return modified content with replacement count"""
        try:
            # Try different encodings
            content = None
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                logger.warning(f"Could not decode file: {file_path}")
                return None, 0
            
            original_content = content
            replacement_count = 0
            
            # Apply all replacement patterns
            for pattern, replacement in self.replacement_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    pattern_replacements = len(matches)
                    replacement_count += pattern_replacements
                    
                    # Track pattern statistics
                    if pattern not in self.stats['replacement_patterns']:
                        self.stats['replacement_patterns'][pattern] = 0
                    self.stats['replacement_patterns'][pattern] += pattern_replacements
                    
                    if pattern_replacements > 0:
                        logger.debug(f"  Applied pattern '{pattern}' -> '{replacement}': {pattern_replacements} times")
            
            return content if content != original_content else None, replacement_count
            
        except Exception as e:
            error_msg = f"Error processing file {file_path}: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return None, 0

    def rename_files_and_directories(self):
        """Rename files and directories containing 'memex'"""
        renamed_items = []
        
        # Find files and directories to rename (bottom-up to handle nested structures)
        items_to_rename = []
        
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            root_path = Path(root)
            
            # Skip backup directory
            if self.backup_dir in root_path.parents or root_path == self.backup_dir:
                continue
            
            # Check files
            for file in files:
                if 'memex' in file.lower() and file not in self.skip_files:
                    items_to_rename.append(root_path / file)
            
            # Check directories
            for dir_name in dirs:
                if 'memex' in dir_name.lower() and dir_name not in self.skip_directories:
                    items_to_rename.append(root_path / dir_name)
        
        # Rename items
        for item_path in items_to_rename:
            try:
                # Create new name by applying replacement patterns to the filename
                old_name = item_path.name
                new_name = old_name
                
                for pattern, replacement in self.replacement_patterns:
                    new_name = re.sub(pattern, replacement, new_name)
                
                if new_name != old_name:
                    new_path = item_path.parent / new_name
                    
                    if not new_path.exists():
                        item_path.rename(new_path)
                        renamed_items.append((str(item_path), str(new_path)))
                        self.stats['files_renamed'] += 1
                        logger.info(f"Renamed: {item_path} -> {new_path}")
                    else:
                        logger.warning(f"Target already exists, skipping rename: {new_path}")
                        
            except Exception as e:
                error_msg = f"Error renaming {item_path}: {e}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)
        
        return renamed_items

    def process_files(self):
        """Process all files for content replacement"""
        files_to_process = self.find_files_to_process()
        logger.info(f"Found {len(files_to_process)} files to process")
        
        for file_path in files_to_process:
            try:
                self.stats['files_processed'] += 1
                
                logger.debug(f"Processing: {file_path}")
                modified_content, replacement_count = self.process_file_content(file_path)
                
                if modified_content is not None and replacement_count > 0:
                    # Write modified content back
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    
                    self.stats['files_modified'] += 1
                    self.stats['total_replacements'] += replacement_count
                    logger.info(f"Modified {file_path}: {replacement_count} replacements")
                
                # Progress indicator
                if self.stats['files_processed'] % 50 == 0:
                    logger.info(f"Progress: {self.stats['files_processed']}/{len(files_to_process)} files processed")
                    
            except Exception as e:
                error_msg = f"Error processing file {file_path}: {e}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)

    def generate_report(self) -> str:
        """Generate a comprehensive replacement report"""
        report = f"""
# Comprehensive Memex to Myndy Replacement Report
Generated: {datetime.now().isoformat()}

## Summary Statistics
- Files Processed: {self.stats['files_processed']}
- Files Modified: {self.stats['files_modified']}
- Files/Directories Renamed: {self.stats['files_renamed']}
- Total Replacements: {self.stats['total_replacements']}
- Errors Encountered: {len(self.stats['errors'])}

## Replacement Patterns Applied
"""
        
        for pattern, count in sorted(self.stats['replacement_patterns'].items(), 
                                   key=lambda x: x[1], reverse=True):
            if count > 0:
                report += f"- `{pattern}`: {count} replacements\n"
        
        if self.stats['errors']:
            report += f"\n## Errors Encountered\n"
            for error in self.stats['errors']:
                report += f"- {error}\n"
        
        report += f"""
## Backup Information
- Backup created at: {self.backup_dir}
- To restore: `rm -rf project/* && cp -r backup_before_replacement/* ./`

## Verification Steps
1. Run tests to ensure functionality
2. Check import statements
3. Verify file references
4. Test pipeline functionality
"""
        
        return report

    def run(self):
        """Execute the comprehensive replacement process"""
        logger.info("=" * 60)
        logger.info("COMPREHENSIVE MEMEX TO MYNDY REPLACEMENT")
        logger.info("=" * 60)
        
        try:
            # Step 1: Create backup
            self.create_backup()
            
            # Step 2: Rename files and directories
            logger.info("Renaming files and directories...")
            renamed_items = self.rename_files_and_directories()
            
            # Step 3: Process file contents
            logger.info("Processing file contents...")
            self.process_files()
            
            # Step 4: Generate report
            report = self.generate_report()
            
            # Save report
            report_path = self.project_root / "memex_to_myndy_replacement_report.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info("=" * 60)
            logger.info("REPLACEMENT COMPLETE!")
            logger.info("=" * 60)
            logger.info(f"Report saved to: {report_path}")
            logger.info(f"Total replacements: {self.stats['total_replacements']}")
            logger.info(f"Files modified: {self.stats['files_modified']}")
            logger.info(f"Files renamed: {self.stats['files_renamed']}")
            
            if self.stats['errors']:
                logger.warning(f"Errors encountered: {len(self.stats['errors'])}")
                logger.warning("Check the report for details")
            
            return True
            
        except Exception as e:
            logger.error(f"Critical error during replacement: {e}")
            return False


def main():
    """Main execution function"""
    try:
        # Initialize replacer
        replacer = ComprehensiveReplacer()
        
        # Confirm execution
        print("⚠️  COMPREHENSIVE MEMEX TO MYNDY REPLACEMENT")
        print("This will modify files throughout the project.")
        print(f"Project root: {replacer.project_root}")
        print(f"Backup will be created at: {replacer.backup_dir}")
        
        response = input("\nProceed with replacement? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            success = replacer.run()
            
            if success:
                print("\n✅ Replacement completed successfully!")
                print("📋 Check the generated report for details")
                print("🔧 Run tests to verify functionality")
            else:
                print("\n❌ Replacement failed!")
                print("🔄 Restore from backup if needed")
        else:
            print("❌ Replacement cancelled")
            
    except KeyboardInterrupt:
        print("\n❌ Replacement interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())