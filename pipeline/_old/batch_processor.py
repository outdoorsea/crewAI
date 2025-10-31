#!/usr/bin/env python3
"""
Batch processor for Myndy AI
Processes commands from a file or stdin
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add paths contextually
CURRENT_DIR = Path(__file__).parent
PIPELINE_ROOT = CURRENT_DIR.parent
MYNDY_AI_ROOT = PIPELINE_ROOT.parent / "myndy-ai"

sys.path.insert(0, str(PIPELINE_ROOT))
if MYNDY_AI_ROOT.exists():
    sys.path.insert(0, str(MYNDY_AI_ROOT))
else:
    # Try alternative paths
    for alt_path in ["../../myndy-ai", "../myndy-ai", "../../../myndy-ai"]:
        abs_alt = (CURRENT_DIR / alt_path).resolve()
        if abs_alt.exists():
            sys.path.insert(0, str(abs_alt))
            break

from crewai_myndy_pipeline import Pipeline

def process_batch(commands_file=None, output_file=None):
    """Process batch commands"""
    pipeline = Pipeline()
    results = []
    
    # Read commands
    if commands_file:
        with open(commands_file, 'r') as f:
            commands = f.readlines()
    else:
        print("Enter commands (one per line, empty line to finish):")
        commands = []
        while True:
            cmd = input("Command: ").strip()
            if not cmd:
                break
            commands.append(cmd)
    
    # Process each command
    for i, command in enumerate(commands, 1):
        command = command.strip()
        if not command or command.startswith('#'):
            continue
            
        print(f"\n[{i}] Processing: {command}")
        
        try:
            messages = [{"role": "user", "content": command}]
            response = pipeline.pipe(
                user_message=command,
                model_id="auto",
                messages=messages,
                body={}
            )
            
            result = {
                "command": command,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            print(f"✅ Response: {response}")
            
        except Exception as e:
            result = {
                "command": command,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
            
            print(f"❌ Error: {e}")
        
        results.append(result)
    
    # Save results
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {output_file}")
    
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch process commands with Myndy AI")
    parser.add_argument("-i", "--input", help="Input file with commands")
    parser.add_argument("-o", "--output", help="Output file for results")
    
    args = parser.parse_args()
    
    try:
        results = process_batch(args.input, args.output)
        print(f"\n🎉 Processed {len(results)} commands")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()