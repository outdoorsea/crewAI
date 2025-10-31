#!/usr/bin/env python3
"""
Single command runner for Myndy AI
Usage: python single_command.py "Your message here" [model_id]
"""

import sys
import json
from pathlib import Path

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

def run_single_command(message, model_id="auto"):
    """Run a single command"""
    try:
        pipeline = Pipeline()
        
        # Create mock message history
        messages = [{"role": "user", "content": message}]
        
        # Process the message
        response = pipeline.pipe(
            user_message=message,
            model_id=model_id,
            messages=messages,
            body={}
        )
        
        return response
    except Exception as e:
        return f"Error: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python single_command.py \"Your message here\" [model_id]")
        print("Example: python single_command.py \"What's the weather like?\"")
        print("Example: python single_command.py \"Search for John Doe\" memory_librarian")
        sys.exit(1)
    
    message = sys.argv[1]
    model_id = sys.argv[2] if len(sys.argv) > 2 else "auto"
    
    print(f"🧠 Myndy AI Processing: {message}")
    print(f"🎯 Using model: {model_id}")
    print("-" * 50)
    
    response = run_single_command(message, model_id)
    print(f"🤖 Response: {response}")

if __name__ == "__main__":
    main()