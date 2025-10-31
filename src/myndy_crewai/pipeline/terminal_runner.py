#!/usr/bin/env python3
"""
Terminal interface for Myndy AI Pipeline
Run conversations directly from the command line
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

class TerminalMyndyAI:
    def __init__(self):
        """Initialize the terminal interface"""
        self.pipeline = Pipeline()
        self.session_messages = []
        print("🧠 Myndy AI Terminal Interface")
        print("=" * 50)
        print("Available models:")
        models = self.pipeline.get_models()
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model['name']}")
        print()
    
    def select_model(self):
        """Let user select a model"""
        models = self.pipeline.get_models()
        while True:
            try:
                choice = input("Select model (1-6, or 'auto' for intelligent routing): ").strip().lower()
                
                if choice == 'auto' or choice == '1':
                    return 'auto'
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(models):
                        return models[idx]['id']
                
                print("❌ Invalid choice. Please try again.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit(0)
    
    def run_conversation(self):
        """Run an interactive conversation"""
        model_id = self.select_model()
        model_name = next((m['name'] for m in self.pipeline.get_models() if m['id'] == model_id), model_id)
        
        print(f"\n🎯 Using: {model_name}")
        print("💬 Start chatting! (Type 'quit' to exit, 'clear' to clear history, 'switch' to change model)")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'clear':
                    self.session_messages = []
                    print("🗑️  Conversation history cleared!")
                    continue
                elif user_input.lower() == 'switch':
                    model_id = self.select_model()
                    model_name = next((m['name'] for m in self.pipeline.get_models() if m['id'] == model_id), model_id)
                    print(f"🎯 Switched to: {model_name}")
                    continue
                elif not user_input:
                    continue
                
                # Add user message to history
                self.session_messages.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Process with pipeline
                print("🤔 Thinking...")
                
                try:
                    response = self.pipeline.pipe(
                        user_message=user_input,
                        model_id=model_id,
                        messages=self.session_messages,
                        body={}
                    )
                    
                    # Add response to history
                    self.session_messages.append({
                        "role": "assistant", 
                        "content": response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    print(f"🤖 Myndy: {response}")
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

def main():
    """Main function"""
    try:
        terminal_ai = TerminalMyndyAI()
        terminal_ai.run_conversation()
    except Exception as e:
        print(f"❌ Failed to start Myndy AI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()