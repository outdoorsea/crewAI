"""
Simple Memory Storage for CrewAI Integration
Provides basic memory storage functionality when full myndy-ai system is not available

File: tools/simple_memory_storage.py
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Simple file-based storage for demo
STORAGE_DIR = Path(__file__).parent / "memory_storage"
STORAGE_DIR.mkdir(exist_ok=True)

ENTITIES_FILE = STORAGE_DIR / "entities.json"
FACTS_FILE = STORAGE_DIR / "facts.json"

def load_storage(file_path: Path) -> Dict[str, Any]:
    """Load data from storage file"""
    try:
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading storage from {file_path}: {e}")
        return {}

def save_storage(file_path: Path, data: Dict[str, Any]) -> bool:
    """Save data to storage file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving storage to {file_path}: {e}")
        return False

def create_entity_simple(name: str, entity_type: str = "person", description: str = "", 
                        organization: str = "", job_title: str = "", email: str = "", 
                        phone: str = "", **kwargs) -> Dict[str, Any]:
    """Create a new entity in simple storage"""
    try:
        logger.info(f"Creating entity: {name} (type: {entity_type})")
        
        # Load existing entities
        entities = load_storage(ENTITIES_FILE)
        
        # Generate unique ID
        entity_id = f"entity_{uuid.uuid4()}"
        
        # Create entity data
        entity_data = {
            "id": entity_id,
            "name": name,
            "type": entity_type,
            "description": description,
            "organization": organization,
            "job_title": job_title,
            "email": email,
            "phone": phone,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Add any additional attributes
        for key, value in kwargs.items():
            if key not in entity_data and value:
                entity_data[key] = value
        
        # Store entity
        entities[entity_id] = entity_data
        
        # Save to file
        if save_storage(ENTITIES_FILE, entities):
            logger.info(f"Successfully created entity {entity_id} for {name}")
            
            # Also create a fact about the organization if provided
            if organization and job_title:
                fact_content = f"{name} works at {organization} as {job_title}"
                add_fact_simple(content=fact_content, entity_id=entity_id, entity_name=name)
            elif organization:
                fact_content = f"{name} is associated with {organization}"
                add_fact_simple(content=fact_content, entity_id=entity_id, entity_name=name)
            
            return {
                "success": True,
                "entity_id": entity_id,
                "name": name,
                "entity_type": entity_type,
                "organization": organization,
                "job_title": job_title,
                "created_at": entity_data["created_at"],
                "message": f"Created entity for {name}"
            }
        else:
            return {
                "success": False,
                "error": "Failed to save entity to storage",
                "name": name
            }
            
    except Exception as e:
        logger.error(f"Error creating entity {name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "name": name
        }

def add_fact_simple(content: str, entity_name: str = "", entity_id: str = "", 
                   source: str = "conversation", confidence: float = 0.8, 
                   verified: bool = False, **kwargs) -> Dict[str, Any]:
    """Add a fact to simple storage"""
    try:
        logger.info(f"Adding fact: {content[:50]}...")
        
        # Load existing facts and entities
        facts = load_storage(FACTS_FILE)
        entities = load_storage(ENTITIES_FILE)
        
        # Find entity if only name provided
        if not entity_id and entity_name:
            for eid, entity in entities.items():
                if entity.get("name", "").lower() == entity_name.lower():
                    entity_id = eid
                    break
            
            if not entity_id:
                # Create new entity if not found
                logger.info(f"Entity not found for {entity_name}, creating new entity")
                result = create_entity_simple(name=entity_name, description=f"Entity created from fact: {content}")
                if result.get("success"):
                    entity_id = result.get("entity_id")
                else:
                    return {
                        "success": False,
                        "error": f"Could not find or create entity for {entity_name}",
                        "content": content
                    }
        
        if not entity_id:
            return {
                "success": False,
                "error": "No entity_id or entity_name provided",
                "content": content
            }
        
        # Generate fact ID
        fact_id = f"fact_{uuid.uuid4()}"
        
        # Create fact data
        fact_data = {
            "id": fact_id,
            "content": content,
            "entity_id": entity_id,
            "entity_name": entities.get(entity_id, {}).get("name", entity_name),
            "source": source,
            "confidence": confidence,
            "verified": verified,
            "created_at": datetime.now().isoformat()
        }
        
        # Store fact
        facts[fact_id] = fact_data
        
        # Save to file
        if save_storage(FACTS_FILE, facts):
            logger.info(f"Successfully added fact to entity {entity_id}")
            return {
                "success": True,
                "fact_id": fact_id,
                "entity_id": entity_id,
                "entity_name": fact_data["entity_name"],
                "fact_content": content,
                "source": source,
                "confidence": confidence,
                "added_at": fact_data["created_at"],
                "message": f"Added fact to {fact_data['entity_name']}"
            }
        else:
            return {
                "success": False,
                "error": "Failed to save fact to storage",
                "content": content
            }
            
    except Exception as e:
        logger.error(f"Error adding fact: {e}")
        return {
            "success": False,
            "error": str(e),
            "content": content
        }

def search_memory_simple(query: str, limit: int = 10, entity_types: List[str] = None, 
                        **kwargs) -> Dict[str, Any]:
    """Search simple storage for entities and facts"""
    try:
        logger.info(f"Searching memory for: {query}")
        
        # Load data
        entities = load_storage(ENTITIES_FILE)
        facts = load_storage(FACTS_FILE)
        
        query_lower = query.lower()
        results = []
        
        # Search entities
        for entity_id, entity in entities.items():
            name = entity.get("name", "").lower()
            description = entity.get("description", "").lower()
            organization = entity.get("organization", "").lower()
            
            if query_lower in name or query_lower in description or query_lower in organization:
                result = {
                    "id": entity_id,
                    "name": entity.get("name", ""),
                    "type": entity.get("type", "person"),
                    "description": entity.get("description", ""),
                    "organization": entity.get("organization", ""),
                    "job_title": entity.get("job_title", ""),
                    "email": entity.get("email", ""),
                    "phone": entity.get("phone", ""),
                    "relevance": "entity_match"
                }
                
                # Add related facts
                entity_facts = []
                for fact_id, fact in facts.items():
                    if fact.get("entity_id") == entity_id:
                        entity_facts.append(fact.get("content", ""))
                
                if entity_facts:
                    result["facts"] = entity_facts[:3]  # Limit to 3 facts
                
                results.append(result)
        
        # Search facts
        for fact_id, fact in facts.items():
            content = fact.get("content", "").lower()
            if query_lower in content:
                entity_id = fact.get("entity_id")
                entity_name = fact.get("entity_name", "Unknown")
                
                result = {
                    "id": fact_id,
                    "type": "fact",
                    "content": fact.get("content", ""),
                    "entity_name": entity_name,
                    "entity_id": entity_id,
                    "source": fact.get("source", ""),
                    "confidence": fact.get("confidence", 0.0),
                    "relevance": "fact_match"
                }
                results.append(result)
        
        # Limit results
        results = results[:limit]
        
        logger.info(f"Found {len(results)} results for query: {query}")
        
        return {
            "success": True,
            "query": query,
            "results_count": len(results),
            "results": results,
            "searched_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "results": []
        }

def get_self_profile_simple(**kwargs) -> Dict[str, Any]:
    """Get user's profile from simple storage"""
    try:
        logger.info("Getting user self profile")
        
        # Search for user profile
        user_result = search_memory_simple("Jeremy Irish", limit=1)
        
        if user_result.get("success") and user_result.get("results"):
            user_info = user_result["results"][0]
            
            profile = {
                "success": True,
                "user_id": user_info.get("id"),
                "name": user_info.get("name"),
                "type": user_info.get("type"),
                "description": user_info.get("description"),
                "organization": user_info.get("organization"),
                "job_title": user_info.get("job_title"),
                "email": user_info.get("email"),
                "phone": user_info.get("phone"),
                "facts": user_info.get("facts", []),
                "retrieved_at": datetime.now().isoformat()
            }
            
            logger.info(f"Retrieved profile for {user_info.get('name')}")
            return profile
        else:
            logger.info("No user profile found in simple storage")
            return {
                "success": True,
                "message": "No user profile found in memory",
                "retrieved_at": datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Error getting self profile: {e}")
        return {
            "success": False,
            "error": str(e)
        }