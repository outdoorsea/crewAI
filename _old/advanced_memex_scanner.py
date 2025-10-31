#!/usr/bin/env python3
"""
Advanced Myndy Scanner and Replacement Analyzer

This script provides advanced scanning capabilities to find ALL instances of "myndy"
in any form throughout the codebase, with detailed analysis and replacement preview.

Features:
- Deep pattern analysis with context
- Case-insensitive and case-sensitive searches
- Regex pattern detection
- Preview mode (show what would be changed)
- Verification mode (scan after replacement)
- Detailed statistics and reporting

Usage: 
    python advanced_memex_scanner.py --scan        # Scan only
    python advanced_memex_scanner.py --preview     # Preview replacements  
    python advanced_memex_scanner.py --replace     # Execute replacements
    python advanced_memex_scanner.py --verify      # Verify no myndy remains

Author: Claude Code Assistant
Date: January 2025
"""

import os
import re
import argparse
import json
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedMemexScanner:
    """Advanced scanner for comprehensive myndy detection and analysis"""
    
    def __init__(self, project_root: str = "/Users/jeremy/crewAI"):
        self.project_root = Path(project_root)
        self.results = {
            'total_files_scanned': 0,
            'files_with_memex': 0,
            'total_instances': 0,
            'patterns_found': defaultdict(list),
            'file_details': {},
            'context_analysis': {},
            'recommendations': []
        }
        
        # Ultra-comprehensive patterns to detect ANY form of myndy
        self.detection_patterns = [
            # Basic word patterns
            (r'myndy', 'basic_lowercase'),
            (r'Myndy', 'basic_titlecase'), 
            (r'MYNDY', 'basic_uppercase'),
            
            # Word boundary patterns
            (r'\bmemex\b', 'word_boundary_lower'),
            (r'\bMemex\b', 'word_boundary_title'),
            (r'\bMEMEX\b', 'word_boundary_upper'),
            
            # CamelCase patterns
            (r'[a-z]myndy[A-Z]', 'camelcase_prefix'),
            (r'[a-z]Myndy[A-Z]', 'camelcase_title_prefix'),
            (r'myndy[A-Z][a-z]', 'camelcase_suffix'),
            (r'Myndy[A-Z][a-z]', 'camelcase_title_suffix'),
            
            # Snake_case patterns
            (r'[a-z_]myndy[a-z_]', 'snakecase_embedded'),
            (r'_memex_', 'snakecase_surrounded'),
            (r'memex_[a-z]', 'snakecase_prefix'),
            (r'[a-z]_memex', 'snakecase_suffix'),
            
            # Kebab-case patterns
            (r'[a-z-]myndy[a-z-]', 'kebabcase_embedded'),
            (r'-myndy-', 'kebabcase_surrounded'),
            (r'myndy-[a-z]', 'kebabcase_prefix'),
            (r'[a-z]-myndy', 'kebabcase_suffix'),
            
            # File extension patterns
            (r'myndy\.(py|js|ts|md|txt|json|yaml|yml)', 'file_extension'),
            (r'\.myndy', 'hidden_file'),
            
            # Path patterns
            (r'/myndy/', 'path_directory'),
            (r'/myndy\b', 'path_ending'),
            (r'\bmemex/', 'path_starting'),
            
            # Comment patterns
            (r'#.*myndy', 'comment_hash'),
            (r'//.*myndy', 'comment_double_slash'),
            (r'/\*.*myndy.*\*/', 'comment_block'),
            (r'""".*myndy.*"""', 'docstring_triple'),
            (r"'''.*myndy.*'''", 'docstring_single'),
            
            # String patterns
            (r'".*myndy.*"', 'string_double_quotes'),
            (r"'.*myndy.*'", 'string_single_quotes'),
            (r'`.*myndy.*`', 'string_backticks'),
            
            # Variable patterns
            (r'[a-zA-Z_][a-zA-Z0-9_]*myndy[a-zA-Z0-9_]*', 'variable_with_memex'),
            (r'myndy[a-zA-Z0-9_]+', 'variable_memex_prefix'),
            (r'[a-zA-Z0-9_]+myndy', 'variable_memex_suffix'),
            
            # Function patterns
            (r'def.*myndy', 'function_definition'),
            (r'function.*myndy', 'function_keyword'),
            (r'myndy.*\(', 'function_call'),
            
            # Class patterns
            (r'class.*myndy', 'class_definition'),
            (r'class.*Myndy', 'class_definition_title'),
            
            # Import patterns
            (r'import.*myndy', 'import_statement'),
            (r'from.*myndy', 'from_import'),
            
            # URL patterns
            (r'http[s]?://.*myndy', 'url_http'),
            (r'www\..*myndy', 'url_www'),
            
            # Configuration patterns
            (r'[a-zA-Z_]*myndy[a-zA-Z_]*\s*[:=]', 'config_assignment'),
            
            # JSON/YAML patterns
            (r'"[^"]*myndy[^"]*":', 'json_key'),
            (r':\s*"[^"]*myndy[^"]*"', 'json_value'),
            
            # Case-insensitive comprehensive search
            (r'(?i)myndy', 'case_insensitive_all'),
        ]
        
        # Replacement mappings for all patterns
        self.replacement_mappings = {
            # Direct replacements
            'myndy': 'myndy',
            'Myndy': 'Myndy', 
            'MYNDY': 'MYNDY',
            
            # Compound patterns
            'myndy_bridge': 'myndy_bridge',
            'Memex_Bridge': 'Myndy_Bridge',
            'MEMEX_BRIDGE': 'MYNDY_BRIDGE',
            'myndyBridge': 'myndyBridge',
            'MyndyBridge': 'MyndyBridge',
            'myndy-bridge': 'myndy-bridge',
            'Myndy-Bridge': 'Myndy-Bridge',
            
            'myndy_tool': 'myndy_tool',
            'Memex_Tool': 'Myndy_Tool',
            'MEMEX_TOOL': 'MYNDY_TOOL',
            'myndyTool': 'myndyTool',
            'MyndyTool': 'MyndyTool',
            'myndy-tool': 'myndy-tool',
            
            'myndy_memory': 'myndy_memory',
            'Memex_Memory': 'Myndy_Memory',
            'MEMEX_MEMORY': 'MYNDY_MEMORY',
            'myndyMemory': 'myndyMemory',
            'MyndyMemory': 'MyndyMemory',
            'myndy-memory': 'myndy-memory',
            
            # Add more compound patterns as needed
        }
        
        # File extensions to scan
        self.scan_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx',
            '.md', '.txt', '.rst', '.doc',
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg',
            '.sh', '.bash', '.zsh', '.fish',
            '.html', '.htm', '.xml', '.css', '.scss', '.sass',
            '.sql', '.db', '.sqlite',
            '.log', '.out', '.err',
            '.env', '.gitignore', '.dockerignore',
            '.csv', '.tsv', '.dat',
            '.r', '.R', '.matlab', '.m',
            '.java', '.c', '.cpp', '.h', '.hpp',
            '.go', '.rust', '.rs', '.php',
            '.rb', '.perl', '.pl',
            '.dockerfile', '.Dockerfile'
        }
        
        # Directories to skip
        self.skip_dirs = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.venv', 'venv', 'env', '.env', 'backup_before_replacement',
            '.claude', 'build', 'dist', '.mypy_cache', '.tox',
            'coverage', '.coverage', '.nyc_output'
        }

    def scan_file(self, file_path: Path) -> Dict:
        """Scan a single file for all myndy patterns"""
        results = {
            'file': str(file_path),
            'instances': [],
            'total_matches': 0,
            'unique_patterns': set()
        }
        
        try:
            # Try multiple encodings
            content = None
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'ascii']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if content is None:
                logger.warning(f"Could not decode {file_path}")
                return results
            
            lines = content.split('\n')
            
            # Apply all detection patterns
            for pattern, pattern_type in self.detection_patterns:
                matches = list(re.finditer(pattern, content, re.MULTILINE))
                
                for match in matches:
                    # Find line number
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.start())
                    if line_end == -1:
                        line_end = len(content)
                    
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = content[line_start:line_end]
                    
                    # Extract context (surrounding lines)
                    context_start = max(0, line_num - 3)
                    context_end = min(len(lines), line_num + 2)
                    context = lines[context_start:context_end]
                    
                    instance = {
                        'pattern': pattern,
                        'pattern_type': pattern_type,
                        'match': match.group(),
                        'line_number': line_num,
                        'line_content': line_content.strip(),
                        'start_pos': match.start(),
                        'end_pos': match.end(),
                        'context': context
                    }
                    
                    results['instances'].append(instance)
                    results['unique_patterns'].add(pattern_type)
                    results['total_matches'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")
            return results

    def scan_all_files(self) -> Dict:
        """Scan all files in the project"""
        logger.info(f"Scanning project: {self.project_root}")
        
        all_files = []
        
        # Find all files to scan
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Include all files (not just by extension) to catch any myndy references
                if (file_path.suffix.lower() in self.scan_extensions or 
                    'myndy' in file.lower() or
                    file_path.suffix == ''):  # Include files without extensions
                    all_files.append(file_path)
        
        logger.info(f"Found {len(all_files)} files to scan")
        
        # Scan each file
        files_with_memex = []
        
        for i, file_path in enumerate(all_files):
            if i % 100 == 0:
                logger.info(f"Progress: {i}/{len(all_files)} files scanned")
            
            file_results = self.scan_file(file_path)
            self.results['total_files_scanned'] += 1
            
            if file_results['total_matches'] > 0:
                self.results['files_with_memex'] += 1
                self.results['total_instances'] += file_results['total_matches']
                self.results['file_details'][str(file_path)] = file_results
                files_with_memex.append(file_path)
                
                # Track pattern usage
                for instance in file_results['instances']:
                    pattern_type = instance['pattern_type']
                    self.results['patterns_found'][pattern_type].append({
                        'file': str(file_path),
                        'line': instance['line_number'],
                        'match': instance['match']
                    })
        
        logger.info("Scan complete!")
        return self.results

    def generate_detailed_report(self) -> str:
        """Generate a comprehensive analysis report"""
        report = f"""# Advanced Myndy Scan Report
Generated: {datetime.now().isoformat()}

## Executive Summary
- **Total Files Scanned**: {self.results['total_files_scanned']:,}
- **Files Containing 'myndy'**: {self.results['files_with_memex']:,}
- **Total Instances Found**: {self.results['total_instances']:,}
- **Unique Pattern Types**: {len(self.results['patterns_found'])}

## Pattern Analysis
"""
        
        # Sort patterns by frequency
        sorted_patterns = sorted(self.results['patterns_found'].items(), 
                               key=lambda x: len(x[1]), reverse=True)
        
        for pattern_type, instances in sorted_patterns:
            count = len(instances)
            report += f"\n### {pattern_type.replace('_', ' ').title()} ({count} instances)\n"
            
            # Show first few examples
            for i, instance in enumerate(instances[:5]):
                report += f"- `{instance['match']}` in {instance['file']}:{instance['line']}\n"
            
            if len(instances) > 5:
                report += f"- ... and {len(instances) - 5} more\n"

        report += "\n## Files Requiring Attention\n"
        
        # Sort files by number of instances
        sorted_files = sorted(self.results['file_details'].items(), 
                            key=lambda x: x[1]['total_matches'], reverse=True)
        
        for file_path, details in sorted_files[:20]:  # Top 20 files
            report += f"\n### {file_path} ({details['total_matches']} instances)\n"
            
            # Group instances by line for better readability
            line_groups = defaultdict(list)
            for instance in details['instances']:
                line_groups[instance['line_number']].append(instance)
            
            for line_num in sorted(line_groups.keys())[:10]:  # First 10 lines
                instances_on_line = line_groups[line_num]
                report += f"**Line {line_num}**: "
                matches = [inst['match'] for inst in instances_on_line]
                report += f"`{', '.join(set(matches))}`\n"
                
                # Show line content
                if instances_on_line:
                    line_content = instances_on_line[0]['line_content']
                    if line_content:
                        report += f"```\n{line_content}\n```\n"

        # Add recommendations
        report += self._generate_recommendations()
        
        return report

    def _generate_recommendations(self) -> str:
        """Generate specific recommendations based on findings"""
        recommendations = "\n## Recommendations\n"
        
        if self.results['total_instances'] == 0:
            recommendations += "✅ **No 'myndy' instances found!** The codebase appears to be clean.\n"
            return recommendations
        
        # Analyze patterns and provide specific advice
        pattern_counts = {k: len(v) for k, v in self.results['patterns_found'].items()}
        
        if pattern_counts.get('word_boundary_lower', 0) > 0:
            recommendations += f"1. **Replace basic 'myndy' words** ({pattern_counts['word_boundary_lower']} instances)\n"
            recommendations += "   - Use pattern: `r'\\bmemex\\b'` → `'myndy'`\n\n"
        
        if pattern_counts.get('word_boundary_title', 0) > 0:
            recommendations += f"2. **Replace title case 'Myndy'** ({pattern_counts['word_boundary_title']} instances)\n"
            recommendations += "   - Use pattern: `r'\\bMemex\\b'` → `'Myndy'`\n\n"
        
        if pattern_counts.get('snakecase_embedded', 0) > 0:
            recommendations += f"3. **Fix snake_case patterns** ({pattern_counts['snakecase_embedded']} instances)\n"
            recommendations += "   - Check for: `myndy_bridge`, `load_myndy_tools`, etc.\n\n"
        
        if pattern_counts.get('import_statement', 0) > 0:
            recommendations += f"4. **Update import statements** ({pattern_counts['import_statement']} instances)\n"
            recommendations += "   - Update module imports and references\n\n"
        
        if pattern_counts.get('file_extension', 0) > 0:
            recommendations += f"5. **Rename files** ({pattern_counts['file_extension']} instances)\n"
            recommendations += "   - Files still have 'myndy' in their names\n\n"
        
        # Priority recommendations
        recommendations += "### High Priority\n"
        high_priority = ['import_statement', 'function_definition', 'class_definition', 'variable_with_memex']
        for pattern in high_priority:
            if pattern in pattern_counts and pattern_counts[pattern] > 0:
                recommendations += f"- Fix {pattern.replace('_', ' ')}: {pattern_counts[pattern]} instances\n"
        
        return recommendations

    def preview_replacements(self) -> str:
        """Preview what replacements would be made"""
        preview = "# Replacement Preview\n\n"
        
        if not self.results['file_details']:
            return preview + "No replacements needed - no 'myndy' instances found.\n"
        
        for file_path, details in self.results['file_details'].items():
            preview += f"## {file_path}\n"
            
            for instance in details['instances'][:10]:  # Show first 10 per file
                original = instance['match']
                # Determine replacement based on pattern
                replacement = self._get_replacement_for_match(original)
                
                preview += f"Line {instance['line_number']}: `{original}` → `{replacement}`\n"
                preview += f"Context: `{instance['line_content']}`\n\n"
        
        return preview

    def _get_replacement_for_match(self, match: str) -> str:
        """Determine the appropriate replacement for a match"""
        # Direct mapping if available
        if match in self.replacement_mappings:
            return self.replacement_mappings[match]
        
        # Pattern-based replacement
        if match.lower() == 'myndy':
            if match.islower():
                return 'myndy'
            elif match.istitle():
                return 'Myndy'
            elif match.isupper():
                return 'MYNDY'
        
        # For complex patterns, apply basic transformation
        return re.sub(r'(?i)myndy', lambda m: 'myndy' if m.group().islower() else 
                     'Myndy' if m.group().istitle() else 'MYNDY', match)

    def save_results(self, output_file: str = None):
        """Save scan results to file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"memex_scan_results_{timestamp}.json"
        
        # Convert sets to lists for JSON serialization
        json_results = dict(self.results)
        json_results['patterns_found'] = dict(json_results['patterns_found'])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, default=str)
        
        logger.info(f"Results saved to: {output_file}")
        return output_file


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Advanced Myndy Scanner and Analyzer")
    parser.add_argument('--scan', action='store_true', help='Scan for myndy instances')
    parser.add_argument('--preview', action='store_true', help='Preview replacements')
    parser.add_argument('--replace', action='store_true', help='Execute replacements')
    parser.add_argument('--verify', action='store_true', help='Verify no myndy remains')
    parser.add_argument('--project-root', default='/Users/jeremy/crewAI', 
                       help='Project root directory')
    parser.add_argument('--output', help='Output file for results')
    
    args = parser.parse_args()
    
    if not any([args.scan, args.preview, args.replace, args.verify]):
        # Default to scan if no action specified
        args.scan = True
    
    scanner = AdvancedMemexScanner(args.project_root)
    
    try:
        if args.scan or args.preview or args.verify:
            print("🔍 Scanning for myndy instances...")
            results = scanner.scan_all_files()
            
            print(f"\n📊 Scan Results:")
            print(f"   Files scanned: {results['total_files_scanned']:,}")
            print(f"   Files with myndy: {results['files_with_memex']:,}")
            print(f"   Total instances: {results['total_instances']:,}")
            
            if args.preview:
                print("\n👁️  Replacement Preview:")
                preview = scanner.preview_replacements()
                print(preview[:2000] + "..." if len(preview) > 2000 else preview)
            
            # Generate and save report
            report = scanner.generate_detailed_report()
            report_file = args.output or f"memex_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"\n📋 Detailed report saved to: {report_file}")
            
            # Save JSON results
            json_file = scanner.save_results(args.output)
            
        if args.replace:
            print("\n⚠️  Replacement mode would require the comprehensive replacement script.")
            print("   Use: python comprehensive_memex_to_myndy_replacement.py")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())