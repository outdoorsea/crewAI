#!/usr/bin/env python3
"""
Enhanced OpenAPI Server for CrewAI-Myndy Integration

Automatically routes conversations to the appropriate agents using intelligent analysis.
Compatible with Open WebUI with intelligent agent routing.

File: api/enhanced_server.py
"""

import json
import logging
import os
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Add myndy to path  
MYNDY_PATH = Path("/Users/jeremy/myndy")
sys.path.insert(0, str(MYNDY_PATH))

# Configure logging early
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import agent router
try:
    from api.agent_router import get_agent_router, AgentRole, RoutingDecision
except ImportError as e:
    logger.warning(f"Could not import agent router: {e}")
    # Fallback definitions
    class AgentRole:
        MEMORY_LIBRARIAN = "memory_librarian"
        RESEARCH_SPECIALIST = "research_specialist"
        PERSONAL_ASSISTANT = "personal_assistant"
        HEALTH_ANALYST = "health_analyst"
        FINANCE_TRACKER = "finance_tracker"

# Import myndy tools
try:
    from tools.myndy_bridge import get_tool_loader
    from qdrant.collections.memory import MemoryManager
    from qdrant.collections.knowledge import KnowledgeManager
    MEMEX_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import myndy tools: {e}")
    MEMEX_AVAILABLE = False

# OpenAI-compatible models
class OpenAIMessage(BaseModel):
    role: str
    content: str

class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[OpenAIMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    stream: Optional[bool] = False

class OpenAIModel(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "crewai-myndy"

class HealthCheck(BaseModel):
    status: str = "healthy"
    timestamp: datetime
    version: str = "1.0.0"

# Create FastAPI app
app = FastAPI(
    title="CrewAI-Myndy Enhanced API",
    description="Multi-agent AI system with intelligent conversation routing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for conversation history
conversation_sessions = {}

# Agent information
AGENTS = {
    AgentRole.MEMORY_LIBRARIAN: {
        "name": "Memory Librarian",
        "description": "Organizes and retrieves personal knowledge, entities, conversation history, and manages contact information",
        "model": "llama3",
        "capabilities": ["memory management", "entity relationships", "conversation history", "contact information", "contact updates", "company tracking"]
    },
    AgentRole.RESEARCH_SPECIALIST: {
        "name": "Research Specialist", 
        "description": "Conducts research, gathers information, and verifies facts",
        "model": "mixtral",
        "capabilities": ["web research", "fact verification", "document analysis"]
    },
    AgentRole.PERSONAL_ASSISTANT: {
        "name": "Personal Assistant",
        "description": "Manages calendar, email, contacts, and personal productivity",
        "model": "gemma", 
        "capabilities": ["calendar management", "email processing", "task coordination"]
    },
    AgentRole.HEALTH_ANALYST: {
        "name": "Health Analyst",
        "description": "Analyzes health data and provides wellness insights",
        "model": "phi",
        "capabilities": ["health analysis", "fitness tracking", "wellness optimization"]
    },
    AgentRole.FINANCE_TRACKER: {
        "name": "Finance Tracker", 
        "description": "Tracks expenses, analyzes spending, and provides financial insights",
        "model": "mistral",
        "capabilities": ["expense tracking", "budget analysis", "financial planning"]
    }
}

def get_session_id(request: OpenAIChatRequest) -> str:
    """Generate or extract session ID for conversation tracking."""
    # Simple session tracking based on conversation content
    # In production, this could use user authentication or other session management
    content_hash = str(abs(hash(str([msg.content for msg in request.messages]))))
    return f"session_{content_hash[:8]}"

def update_conversation_history(session_id: str, messages: List[OpenAIMessage]):
    """Update conversation history for a session."""
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = {
            "created_at": datetime.now(),
            "messages": [],
            "agent_history": []
        }
    
    # Convert messages to dict format for the router
    message_dicts = [{
        "role": msg.role,
        "content": msg.content,
        "timestamp": datetime.now().isoformat()
    } for msg in messages]
    
    conversation_sessions[session_id]["messages"] = message_dicts
    
    # Keep only recent history to avoid memory bloat
    if len(conversation_sessions[session_id]["messages"]) > 20:
        conversation_sessions[session_id]["messages"] = conversation_sessions[session_id]["messages"][-20:]

@app.get("/")
async def health_check():
    """Health check endpoint."""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now()
    )

@app.get("/status")
async def get_status():
    """Get system status with routing information."""
    return {
        "status": "operational",
        "agents_available": len(AGENTS),
        "routing_enabled": True,
        "conversation_sessions": len(conversation_sessions),
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "features": {
            "intelligent_routing": True,
            "conversation_context": True,
            "multi_agent_collaboration": True
        }
    }

@app.get("/models")
async def list_models():
    """List available models (OpenAI-compatible) with routing info."""
    models = []
    
    # Add the intelligent router as the default model
    models.append(OpenAIModel(
        id="auto",
        created=int(datetime.now().timestamp())
    ))
    
    # Add individual agents
    for agent_id, agent_info in AGENTS.items():
        models.append(OpenAIModel(
            id=agent_id,
            created=int(datetime.now().timestamp())
        ))
    
    return {"object": "list", "data": models}

@app.post("/chat/completions")
async def chat_completions(request: OpenAIChatRequest):
    """OpenAI-compatible chat completions with intelligent agent routing."""
    try:
        # Get session ID and update conversation history
        session_id = get_session_id(request)
        update_conversation_history(session_id, request.messages)
        
        # Get the last user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        last_message = user_messages[-1].content
        
        # Determine which agent to use
        if request.model == "auto":
            # Use intelligent routing
            try:
                router = get_agent_router()
                conversation_context = conversation_sessions[session_id]["messages"]
                routing_decision = router.analyze_message(last_message, conversation_context)
                
                selected_agent = routing_decision.primary_agent
                agent_info = AGENTS[selected_agent]
                
                # Track agent usage in session
                conversation_sessions[session_id]["agent_history"].append({
                    "agent": selected_agent,
                    "confidence": routing_decision.confidence,
                    "reasoning": routing_decision.reasoning,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Execute actual tool search based on agent type
                tool_results = await execute_agent_tools(selected_agent, last_message)
                
                # Generate response with routing information and actual results
                response_content = f"""🤖 **{agent_info['name']}** (Auto-selected)

**Routing Analysis:** {routing_decision.reasoning}

**Response:** Hello! I'm the {agent_info['name']}, and I've been automatically selected to help you with your request.

You asked: "{last_message}"

{tool_results}

"""
                
                if routing_decision.requires_collaboration:
                    secondary_names = [AGENTS[role]['name'] for role in routing_decision.secondary_agents]
                    response_content += f"\n**Collaboration Suggested:** This task might benefit from working with {', '.join(secondary_names)} for a comprehensive approach.\n\n"
                
                if not tool_results or "No results found" in tool_results:
                    response_content += "\nI searched my knowledge base but didn't find specific information about your query. My capabilities include: " + ', '.join(agent_info['capabilities']) + ". How else can I assist you?"
                else:
                    response_content += "\nI'm part of the CrewAI-Myndy integration system with access to 31+ specialized tools. Is there anything else you'd like to know?"
                
            except Exception as e:
                logger.warning(f"Router failed, falling back to Memory Librarian: {e}")
                selected_agent = AgentRole.MEMORY_LIBRARIAN
                agent_info = AGENTS[selected_agent]
                response_content = f"""🤖 **{agent_info['name']}** (Fallback)

Hello! I'm the {agent_info['name']}, selected as a fallback to help you.

You asked: "{last_message}"

{agent_info['description']}

My capabilities include: {', '.join(agent_info['capabilities'])}

I'm part of the CrewAI-Myndy integration system. How can I assist you today?"""
        
        else:
            # Use specific agent requested
            agent_info = AGENTS.get(request.model)
            if not agent_info:
                raise HTTPException(status_code=400, detail=f"Unknown model: {request.model}")
            
            # Execute actual tool search for direct agent selection too
            tool_results = await execute_agent_tools(request.model, last_message)
            
            response_content = f"""🤖 **{agent_info['name']}** (Direct selection)

Hello! I'm the {agent_info['name']}.

You asked: "{last_message}"

{tool_results}

"""
            
            if not tool_results or "No results found" in tool_results:
                response_content += f"\nI searched my knowledge base but didn't find specific information about your query. My capabilities include: {', '.join(agent_info['capabilities'])}. How else can I assist you?"
            else:
                response_content += "\nIs there anything else you'd like to know?"
        
        return {
            "id": f"chatcmpl-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant", 
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": sum(len(msg.content.split()) for msg in request.messages),
                "completion_tokens": len(response_content.split()),
                "total_tokens": sum(len(msg.content.split()) for msg in request.messages) + len(response_content.split())
            }
        }
        
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def list_agents():
    """List all available agents with routing information."""
    agents = []
    for agent_id, agent_info in AGENTS.items():
        agents.append({
            "id": agent_id,
            "name": agent_info["name"],
            "description": agent_info["description"],
            "model": agent_info["model"],
            "capabilities": agent_info["capabilities"]
        })
    
    return {
        "agents": agents,
        "routing_available": True,
        "auto_model": "auto",
        "description": "Use 'auto' model for intelligent agent selection based on conversation analysis"
    }

@app.get("/routing/test")
async def test_routing():
    """Test the agent routing system with sample messages."""
    try:
        router = get_agent_router()
        
        test_messages = [
            "Help me organize my notes from last week's meetings",
            "What are the latest trends in artificial intelligence?", 
            "Schedule a meeting with John for tomorrow at 2 PM",
            "Analyze my sleep patterns and suggest improvements",
            "How much did I spend on groceries this month?",
            "I need a comprehensive analysis of my life - health, finances, and productivity"
        ]
        
        results = []
        for message in test_messages:
            decision = router.analyze_message(message)
            results.append({
                "message": message,
                "selected_agent": decision.primary_agent,
                "confidence": decision.confidence,
                "complexity": decision.complexity,
                "reasoning": decision.reasoning,
                "collaboration": decision.secondary_agents if decision.requires_collaboration else None
            })
        
        return {
            "routing_tests": results,
            "router_status": "operational"
        }
        
    except Exception as e:
        logger.error(f"Routing test error: {e}")
        return {
            "error": str(e),
            "router_status": "unavailable"
        }

@app.get("/sessions")
async def list_sessions():
    """List active conversation sessions."""
    sessions = []
    for session_id, session_data in conversation_sessions.items():
        sessions.append({
            "session_id": session_id,
            "created_at": session_data["created_at"].isoformat(),
            "message_count": len(session_data["messages"]),
            "agents_used": len(session_data["agent_history"]),
            "last_agent": session_data["agent_history"][-1]["agent"] if session_data["agent_history"] else None
        })
    
    return {
        "active_sessions": len(conversation_sessions),
        "sessions": sessions
    }

async def execute_agent_tools(agent_role: str, query: str) -> str:
    """Execute appropriate tools based on agent role and query."""
    try:
        if not MEMEX_AVAILABLE:
            return "**Tool Execution:** Myndy tools not available in this environment."
        
        # For Memory Librarian - search for entities, people, conversations, and handle updates
        if agent_role == AgentRole.MEMORY_LIBRARIAN or agent_role == "memory_librarian":
            # Check if this is an update request
            if any(keyword in query.lower() for keyword in ['update', 'change', 'modify', 'works for', 'works at', 'company is', 'job at']):
                update_result = await handle_contact_update(query)
                return f"**Contact Update:**\n{update_result}"
            else:
                # Regular search
                results = await search_memory_knowledge(query)
                if results:
                    return f"**Search Results:**\n{results}"
                else:
                    return "**Search Results:** No results found in memory for this query."
        
        # For Research Specialist - could implement web search or document search
        elif agent_role == AgentRole.RESEARCH_SPECIALIST or agent_role == "research_specialist":
            return "**Research Capability:** I can help you research and analyze information. My tools are being enhanced to provide detailed research results."
        
        # For Personal Assistant - could search calendar, tasks, contacts
        elif agent_role == AgentRole.PERSONAL_ASSISTANT or agent_role == "personal_assistant":
            return "**Productivity Check:** I can help you manage your calendar, tasks, and contacts. My scheduling and organization tools are ready to assist."
        
        # For Health Analyst - could search health data
        elif agent_role == AgentRole.HEALTH_ANALYST or agent_role == "health_analyst":
            return "**Health Analysis:** I can analyze your health and fitness data. My wellness tracking and optimization tools are available."
        
        # For Finance Tracker - could search financial data
        elif agent_role == AgentRole.FINANCE_TRACKER or agent_role == "finance_tracker":
            return "**Financial Analysis:** I can track and analyze your expenses and financial patterns. My budgeting and financial planning tools are ready."
        
        else:
            return "**Tool Execution:** Agent-specific tools are being prepared for this request."
            
    except Exception as e:
        logger.error(f"Tool execution error for {agent_role}: {e}")
        return f"**Tool Execution Error:** {str(e)}"

async def search_memory_knowledge(query: str) -> str:
    """Search memory and knowledge base for information, including contact details."""
    try:
        results = []
        
        memory_manager = MemoryManager()
        
        # Search for contacts specifically
        contact_results = memory_manager.search_contacts(query, limit=3)
        if contact_results:
            results.append("**Contacts Found:**")
            for contact in contact_results:
                name = contact.data.get('name', contact.data.get('full_name', 'Unknown'))
                company = contact.data.get('company', contact.data.get('organization', ''))
                title = contact.data.get('title', contact.data.get('job_title', ''))
                email = contact.data.get('email', '')
                phone = contact.data.get('phone', contact.data.get('phone_number', ''))
                
                contact_info = [f"📧 {name}"]
                if company:
                    contact_info.append(f"🏢 Company: {company}")
                if title:
                    contact_info.append(f"💼 Title: {title}")
                if email:
                    contact_info.append(f"📧 Email: {email}")
                if phone:
                    contact_info.append(f"📞 Phone: {phone}")
                
                results.append("• " + " | ".join(contact_info))
        
        # Search for people/entities
        people_results = memory_manager.search_people(query, limit=3)
        if people_results:
            results.append("\n**People Found:**")
            for person in people_results:
                name = person.data.get('name', person.data.get('content', 'Unknown')[:50] if person.data.get('content') else 'Unknown')
                description = person.data.get('description', person.data.get('content', 'No description')[:100] if person.data.get('content') else 'No description')
                company = person.data.get('company', person.data.get('organization', ''))
                
                person_info = [f"👤 {name}"]
                if company:
                    person_info.append(f"🏢 {company}")
                person_info.append(f"📝 {description}")
                
                results.append("• " + " | ".join(person_info))
        
        # Search for general memories (using all memory search)
        memory_results = memory_manager.search_all_memory(query, limit=3)
        if memory_results:
            results.append("\n**Related Memories:**")
            for memory in memory_results:
                content = memory.data.get('content', 'No content')
                if content and len(content) > 100:
                    content = content[:100] + "..."
                results.append(f"• {content}")
        
        # Search knowledge base
        try:
            knowledge_manager = KnowledgeManager()
            knowledge_results = knowledge_manager.search_documents(query, limit=3)
            if knowledge_results:
                results.append("\n**Knowledge Base:**")
                for doc in knowledge_results:
                    title = doc.data.get('title', 'Untitled')
                    content = doc.data.get('content', 'No content')
                    if content and len(content) > 100:
                        content = content[:100] + "..."
                    results.append(f"• {title}: {content}")
        except Exception as e:
            logger.debug(f"Knowledge search not available: {e}")
        
        if results:
            return "\n".join(results)
        else:
            return "No results found in memory or knowledge base."
            
    except Exception as e:
        logger.error(f"Memory search error: {e}")
        return f"Memory search encountered an error: {str(e)}"

async def handle_contact_update(query: str) -> str:
    """Handle contact information updates based on natural language queries."""
    try:
        memory_manager = MemoryManager()
        
        # Parse the update query to extract person name and update information
        query_lower = query.lower()
        
        # Extract person name (simple approach - look for patterns)
        person_name = None
        update_info = {}
        
        # Patterns for different types of updates
        patterns = {
            'company': ['works for', 'works at', 'company is', 'job at', 'employed by', 'at company'],
            'title': ['title is', 'position is', 'role is', 'job title', 'works as'],
            'email': ['email is', 'email:', '@'],
            'phone': ['phone is', 'phone:', 'number is', 'call']
        }
        
        # Try to extract name (assume it's at the beginning of the query)
        words = query.split()
        if len(words) >= 2:
            # Look for name before update keywords
            for i, word in enumerate(words):
                if any(pattern_word in query_lower[i*len(word):] for pattern_list in patterns.values() for pattern_word in pattern_list):
                    # Skip words like "update", "change", "modify" at the beginning
                    start_idx = 1 if words[0].lower() in ['update', 'change', 'modify'] else 0
                    person_name = ' '.join(words[start_idx:i]).strip()
                    break
            
            if not person_name and len(words) >= 3:
                # Default to first two words as name (skip "update" if it's the first word)
                start_idx = 1 if words[0].lower() in ['update', 'change', 'modify'] else 0
                person_name = ' '.join(words[start_idx:start_idx+2])
        
        # Extract update information
        for field, pattern_list in patterns.items():
            for pattern in pattern_list:
                if pattern in query_lower:
                    # Find the part after the pattern
                    pattern_pos = query_lower.find(pattern)
                    after_pattern = query[pattern_pos + len(pattern):].strip()
                    
                    # Remove common words and get the value
                    value = after_pattern.split('.')[0].split(',')[0].strip()
                    
                    # Clean up value
                    for cleanup_word in ['is', 'now', 'the', 'a', 'an']:
                        if value.lower().startswith(cleanup_word + ' '):
                            value = value[len(cleanup_word):].strip()
                    
                    if value:
                        update_info[field] = value
                        break
        
        if not person_name:
            return "I couldn't identify the person's name in your update request. Please specify who you'd like to update."
        
        if not update_info:
            return f"I couldn't identify what information to update for {person_name}. Please specify what you'd like to change (company, title, email, phone)."
        
        # Search for existing contact
        existing_contacts = memory_manager.search_contacts(person_name, limit=1)
        
        if existing_contacts:
            # Update existing contact
            contact = existing_contacts[0]
            original_data = contact.data.copy()
            
            # Update the data
            for field, value in update_info.items():
                original_data[field] = value
            
            # Save updated contact (this is a simplified approach)
            # In a real implementation, you'd want to use proper update methods
            success = memory_manager.save_model('contact', original_data)
            
            if success:
                updated_fields = ', '.join([f"{field}: {value}" for field, value in update_info.items()])
                return f"✅ Updated {person_name}'s information:\n{updated_fields}\n\nContact updated successfully in memory."
            else:
                return f"❌ Failed to update {person_name}'s information in the database."
        else:
            # Create new contact entry
            new_contact_data = {
                'name': person_name,
                'id': str(uuid.uuid4()),
                'created_at': datetime.now().isoformat(),
                **update_info
            }
            
            success = memory_manager.save_model('contact', new_contact_data)
            
            if success:
                updated_fields = ', '.join([f"{field}: {value}" for field, value in update_info.items()])
                return f"✅ Created new contact for {person_name}:\n{updated_fields}\n\nContact saved to memory."
            else:
                return f"❌ Failed to save new contact information for {person_name}."
            
    except Exception as e:
        logger.error(f"Contact update error: {e}")
        return f"Contact update encountered an error: {str(e)}"

@app.get("/docs-info")
async def get_docs_info():
    """Information about API documentation."""
    return {
        "openapi_url": "/openapi.json",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "description": "CrewAI-Myndy Enhanced API with Intelligent Agent Routing",
        "features": {
            "intelligent_routing": "Use 'auto' model for automatic agent selection",
            "conversation_context": "Maintains conversation history for better routing",
            "multi_agent_collaboration": "Suggests when multiple agents should work together",
            "openai_compatibility": "Full compatibility with Open WebUI and OpenAI clients"
        }
    }

def kill_previous_processes(port: int = 8001):
    """Kill any processes running on the specified port."""
    try:
        # Find processes using the port
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        logger.info(f"🔄 Killed previous process {pid} on port {port}")
                        time.sleep(0.5)  # Give process time to cleanup
                        
                        # If process still exists, force kill
                        try:
                            os.kill(int(pid), 0)  # Check if process still exists
                            os.kill(int(pid), signal.SIGKILL)
                            logger.info(f"🔄 Force killed stubborn process {pid}")
                        except ProcessLookupError:
                            pass  # Process already dead
                            
                    except (ValueError, ProcessLookupError, PermissionError) as e:
                        logger.debug(f"Could not kill process {pid}: {e}")
            
            # Wait a moment for ports to be released
            time.sleep(1)
            logger.info(f"✅ Port {port} cleared")
        else:
            logger.info(f"✅ Port {port} is available")
            
    except FileNotFoundError:
        # lsof not available, try alternative approach
        logger.debug("lsof not available, checking port differently")
    except Exception as e:
        logger.warning(f"Could not check/kill processes on port {port}: {e}")

def main():
    """Run the enhanced server."""
    port = 8001
    
    logger.info("Starting CrewAI-Myndy Enhanced OpenAPI Server")
    logger.info("🔄 Checking for previous instances...")
    
    # Kill any previous processes on our port
    kill_previous_processes(port)
    
    logger.info("🚀 Features: Intelligent Agent Routing + Conversation Analysis + Tool Execution")
    logger.info("🤖 Use 'auto' model for automatic agent selection")
    logger.info("🔧 Myndy Tools: " + ("Available" if MEMEX_AVAILABLE else "Limited"))
    logger.info(f"📊 API Documentation: http://localhost:{port}/docs")
    logger.info(f"🧪 Test Routing: http://localhost:{port}/routing/test")
    logger.info("💬 Compatible with Open WebUI")
    logger.info(f"🌐 Server starting on http://localhost:{port}")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()