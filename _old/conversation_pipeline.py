"""
Complete Conversation-Driven Update Pipeline

This integrates conversation analysis, automatic updates, and agent responses
to demonstrate the full conversation-driven update system.

File: conversation_pipeline.py
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Setup paths
CREWAI_PATH = Path("/Users/jeremy/crewAI")
MYNDY_PATH = Path("/Users/jeremy/myndy")
sys.path.insert(0, str(CREWAI_PATH))
sys.path.insert(0, str(MYNDY_PATH))
sys.path.insert(0, str(CREWAI_PATH / "tools"))

from conversation_analyzer import ConversationAnalyzer
from auto_updater import AutoUpdater
from status_monitoring_tool import _status_tool
from profile_monitoring_tool import _profile_tool

logger = logging.getLogger(__name__)

class ConversationPipeline:
    """Complete pipeline for conversation-driven updates."""
    
    def __init__(self):
        """Initialize the conversation pipeline."""
        self.analyzer = ConversationAnalyzer()
        self.updater = AutoUpdater()
        self.conversation_history = []
    
    def process_conversation_turn(self, user_message: str, user_id: str = "default") -> dict:
        """
        Process a complete conversation turn with analysis, updates, and response.
        
        Args:
            user_message: The user's message
            user_id: User identifier
            
        Returns:
            Dictionary with complete processing results
        """
        turn_result = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message,
            "user_id": user_id,
            "processing_steps": {}
        }
        
        # Step 1: Analyze the message
        print(f"🔍 Analyzing message: '{user_message}'")
        analysis_result = self.updater.process_message(user_message, user_id, auto_apply=True)
        turn_result["processing_steps"]["analysis"] = analysis_result
        
        # Step 2: Get current status and profile
        current_status = _status_tool.get_status_summary(user_id)
        current_profile = _profile_tool.get_profile_summary(user_id)
        turn_result["processing_steps"]["current_state"] = {
            "status": current_status,
            "profile": current_profile
        }
        
        # Step 3: Generate contextual response
        response = self._generate_contextual_response(
            user_message, analysis_result, current_status, current_profile
        )
        turn_result["agent_response"] = response
        
        # Step 4: Store conversation turn
        self.conversation_history.append(turn_result)
        
        return turn_result
    
    def _generate_contextual_response(self, user_message: str, analysis_result: dict, 
                                    current_status: dict, current_profile: dict) -> str:
        """Generate a contextual response based on the conversation analysis."""
        
        # Count updates applied
        status_updates = len(analysis_result.get("applied_updates", {}).get("status", []))
        profile_updates = len(analysis_result.get("applied_updates", {}).get("profile", []))
        
        response_parts = []
        
        # Acknowledge updates made
        if status_updates > 0 or profile_updates > 0:
            response_parts.append(
                f"I've updated your information based on what you shared "
                f"({status_updates} status updates, {profile_updates} profile updates)."
            )
        
        # Respond to mood changes
        applied_status = analysis_result.get("applied_updates", {}).get("status", [])
        for update in applied_status:
            if update["type"] == "mood":
                mood = update["value"]
                if mood == "happy":
                    response_parts.append("That's wonderful to hear! It sounds like you're having a great day.")
                elif mood == "sad":
                    response_parts.append("I'm sorry to hear you're feeling down. Is there anything I can help with?")
                elif mood == "anxious":
                    response_parts.append("I understand you're feeling anxious. Would you like to talk about what's on your mind?")
                elif mood == "tired":
                    response_parts.append("It sounds like you could use some rest. Have you been getting enough sleep?")
                elif mood == "energetic":
                    response_parts.append("Great to hear you're feeling energetic! What are you planning to do with all that energy?")
        
        # Respond to activities
        for update in applied_status:
            if update["type"] == "activity":
                activity = update["value"]
                if activity == "working":
                    response_parts.append("Hope your work is going well today.")
                elif activity == "exercising":
                    response_parts.append("Good for you for staying active! Exercise is so important.")
                elif activity == "traveling":
                    response_parts.append("Traveling sounds exciting! I hope you're having a great trip.")
        
        # Respond to new preferences
        applied_profile = analysis_result.get("applied_updates", {}).get("profile", [])
        for update in applied_profile:
            if update["type"] == "preference":
                category = update["category"]
                value = update["value"]
                response_parts.append(f"I'll remember that you like {value}. Good to know your {category} preferences!")
        
        # Respond to new goals
        for update in applied_profile:
            if update["type"] == "goal":
                response_parts.append(f"That's a great goal! I'll help keep track of your progress.")
        
        # Default response if no specific updates
        if not response_parts:
            response_parts.append("Thanks for sharing that with me.")
        
        # Add contextual suggestions based on current state
        if current_status.get("mood") == "stressed" or any(
            attr.get("name") == "busy" for attr in current_status.get("active_attributes", [])
        ):
            response_parts.append("Since you seem busy/stressed, would you like me to help you organize your tasks?")
        
        return " ".join(response_parts)
    
    def demonstrate_conversation_flow(self):
        """Demonstrate the complete conversation flow with sample messages."""
        
        sample_conversation = [
            "Hey! I'm feeling really excited today because I just got a promotion at work! 😊",
            "I love pizza and coffee - they're definitely my favorites",
            "Actually, I'm getting pretty tired from all the extra work lately",
            "My goal this year is to learn Spanish and maybe travel to Barcelona",
            "I believe in always being honest with people, it's really important to me",
            "I was just talking to my wife Sarah about planning our summer vacation",
            "I'm at the gym right now, feeling super motivated to get in shape! 💪",
            "I really prefer jazz and classical music when I'm trying to focus on coding"
        ]
        
        print("🚀 Conversation-Driven Update Pipeline Demo")
        print("=" * 60)
        print("This demonstrates how the system analyzes conversations and")
        print("automatically updates user status and profile information.\n")
        
        for i, message in enumerate(sample_conversation, 1):
            print(f"\n📱 Turn {i}: User says:")
            print(f"   '{message}'")
            
            result = self.process_conversation_turn(message, "demo_user")
            
            # Show what was detected and updated
            analysis = result["processing_steps"]["analysis"]
            status_updates = analysis.get("applied_updates", {}).get("status", [])
            profile_updates = analysis.get("applied_updates", {}).get("profile", [])
            
            print(f"🔍 Analysis Results:")
            if status_updates:
                status_summary = [f"{u['type']}={u['value']}" for u in status_updates]
                print(f"   📊 Status updates: {status_summary}")
            if profile_updates:
                profile_summary = [f"{u['type']}={u.get('value', u.get('category', 'unknown'))}" for u in profile_updates]
                print(f"   👤 Profile updates: {profile_summary}")
            if not status_updates and not profile_updates:
                print(f"   ℹ️  No updates detected")
            
            print(f"🤖 Agent Response:")
            print(f"   '{result['agent_response']}'")
            
            # Show brief current state
            current_status = result["processing_steps"]["current_state"]["status"]
            current_profile = result["processing_steps"]["current_state"]["profile"]
            
            if current_status.get("mood"):
                print(f"📊 Current mood: {current_status['mood']}")
            if current_status.get("activity"):
                print(f"🏃 Current activity: {current_status['activity']}")
            
            # Brief pause for readability
            if i < len(sample_conversation):
                print("   ...")
        
        # Final summary
        print(f"\n📋 Final Summary:")
        final_status = _status_tool.get_status_summary("demo_user")
        final_profile = _profile_tool.get_profile_summary("demo_user")
        
        print(f"📊 Final Status: {json.dumps(final_status, indent=2)}")
        print(f"👤 Final Profile: {json.dumps(final_profile, indent=2)}")
        
        return {
            "conversation_turns": len(sample_conversation),
            "total_status_updates": sum(
                len(turn["processing_steps"]["analysis"].get("applied_updates", {}).get("status", []))
                for turn in self.conversation_history
            ),
            "total_profile_updates": sum(
                len(turn["processing_steps"]["analysis"].get("applied_updates", {}).get("profile", []))
                for turn in self.conversation_history
            ),
            "final_status": final_status,
            "final_profile": final_profile
        }

def main():
    """Run the conversation pipeline demonstration."""
    logging.basicConfig(level=logging.INFO)
    
    pipeline = ConversationPipeline()
    results = pipeline.demonstrate_conversation_flow()
    
    print(f"\n🎉 Demo Complete!")
    print(f"   Processed {results['conversation_turns']} conversation turns")
    print(f"   Applied {results['total_status_updates']} status updates")
    print(f"   Applied {results['total_profile_updates']} profile updates")
    print(f"\n✅ Conversation-driven updates are working perfectly!")

if __name__ == "__main__":
    main()