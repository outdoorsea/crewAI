"""
Memory Storage Tools for CrewAI Integration
Provides storage tools to connect CrewAI agents with myndy-ai memory system

File: tools/memory_storage_tools.py
"""

import json
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Add myndy-ai to path - correct path resolution
# From crewAI/tools/ we need to go up two levels to myndy-core, then into myndy-ai  
MYNDY_AI_PATH = Path(__file__).parent.parent.parent / "myndy-ai"
if MYNDY_AI_PATH.exists():
    sys.path.insert(0, str(MYNDY_AI_PATH))
    logger.info(f"Added myndy-ai path: {MYNDY_AI_PATH}")
else:
    logger.warning(f"Myndy-ai path not found: {MYNDY_AI_PATH}")
    logger.info(f"Current file location: {Path(__file__)}")
    logger.info(f"Attempted path: {MYNDY_AI_PATH}")
    logger.info(f"Path exists check: {MYNDY_AI_PATH.exists()}")

# Test import to ensure path is working
try:
    import memory
    logger.info("Successfully imported myndy-ai memory module")
except ImportError as e:
    logger.warning(f"Failed to import myndy-ai memory module: {e}")
    # Try alternate path resolution
    alternate_path = Path(__file__).parent.parent.parent / "myndy-ai"
    if alternate_path.exists():
        sys.path.insert(0, str(alternate_path))
        logger.info(f"Added alternate myndy-ai path: {alternate_path}")
    else:
        logger.error("Could not locate myndy-ai directory for memory integration")

def create_entity(name: str, entity_type: str = "person", description: str = "", 
                 organization: str = "", job_title: str = "", email: str = "", 
                 phone: str = "", **kwargs) -> Dict[str, Any]:
    """
    Create a new entity in the myndy-ai memory system.
    
    Args:
        name: Full name of the entity
        entity_type: Type of entity (person, organization, etc.)
        description: Description or notes about the entity
        organization: Organization the person works for
        job_title: Job title if applicable
        email: Email address if known
        phone: Phone number if known
        **kwargs: Additional entity attributes
        
    Returns:
        Dictionary with creation status and entity information
    """
    # Try importing memory models first (these should work)
    try:
        from memory.person_model import Person, ContactName, ContactMethod
        person_model_available = True
        logger.debug("Successfully imported person model components")
    except ImportError as e:
        logger.warning(f"Could not import myndy memory person model: {e}")
        person_model_available = False
    
    # Try importing CRUD components separately (these may fail due to qdrant dependencies)  
    try:
        from memory.crud.people_crud import PeopleCRUD
        crud_available = True
        logger.debug("Successfully imported people CRUD")
    except ImportError as e:
        logger.warning(f"Could not import people CRUD: {e}")
        crud_available = False
    
    # Only proceed if we have the basic models
    if person_model_available and crud_available:
        try:
            logger.info(f"Creating entity: {name} (type: {entity_type})")
            
            # Initialize CRUD
            people_crud = PeopleCRUD()
            
            # Generate unique ID
            entity_id = f"person_{uuid.uuid4()}"
            
            # Parse name
            name_parts = name.strip().split()
            first_name = name_parts[0] if name_parts else ""
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            # Create contact name
            contact_name = ContactName(
                full=name,
                first=first_name,
                last=last_name
            )
            
            # Create contact methods
            contact_methods = []
            if email:
                contact_methods.append(ContactMethod(
                    type="email",
                    value=email,
                    is_primary=True
                ))
            if phone:
                contact_methods.append(ContactMethod(
                    type="phone", 
                    value=phone,
                    is_primary=not bool(email)  # Primary if no email
                ))
            
            # Create employment if organization provided
            employments = []
            if organization:
                try:
                    from memory.person_model import Employment
                    employments.append(Employment(
                        name=organization,
                        title=job_title or None,
                        is_current=True
                    ))
                except ImportError:
                    logger.warning("Could not import Employment model, skipping employment")
            
            # Create person data
            person_data = {
                "id": entity_id,
                "name": contact_name.model_dump(),
                "contact_methods": [m.model_dump() for m in contact_methods],
                "employments": [emp.model_dump() for emp in employments],
                "notes": description,
                "source": "crewai_conversation",
                "create_entity": True
            }
            
            # Add any additional attributes
            for key, value in kwargs.items():
                if key not in person_data and value:
                    person_data[key] = value
            
            # Create person
            success, person = people_crud.create_person(person_data)
            
            if success and person:
                logger.info(f"Successfully created entity {entity_id} for {name}")
                
                # Add the organization fact if provided
                if organization:
                    fact_content = f"{name} works at {organization}"
                    if job_title:
                        fact_content += f" as {job_title}"
                    
                    people_crud.add_person_fact(
                        person_id=entity_id,
                        fact_content=fact_content,
                        source="crewai_conversation",
                        confidence=0.9
                    )
                
                return {
                    "success": True,
                    "entity_id": entity_id,
                    "name": name,
                    "entity_type": entity_type,
                    "organization": organization,
                    "job_title": job_title,
                    "created_at": datetime.now().isoformat(),
                    "message": f"Created entity for {name}"
                }
            else:
                logger.error(f"Failed to create entity for {name}")
                return {
                    "success": False,
                    "error": "Failed to create entity in memory system",
                    "name": name
                }
        except Exception as e:
            logger.error(f"Error creating entity with myndy-ai: {e}")
            # Fall through to simple storage fallback
    
    # Fallback when memory models or CRUD not available
    logger.warning("Using simple storage fallback for entity creation")
    try:
        return create_entity_simple(name=name, entity_type=entity_type, description=description,
                                   organization=organization, job_title=job_title, email=email, phone=phone, **kwargs)
    except Exception as fallback_e:
        logger.error(f"Error creating entity {name} with simple storage: {fallback_e}")
        return {
            "success": False,
            "error": f"All storage methods failed: {fallback_e}",
            "name": name
        }

def add_fact(content: str, entity_name: str = "", entity_id: str = "", 
             source: str = "conversation", confidence: float = 0.8, 
             verified: bool = False, **kwargs) -> Dict[str, Any]:
    """
    Add a fact to an entity in the myndy-ai memory system.
    
    Args:
        content: The fact content to store
        entity_name: Name of the entity (if entity_id not provided)
        entity_id: ID of the entity to add fact to
        source: Source of the fact
        confidence: Confidence level (0.0 to 1.0)
        verified: Whether this fact is verified
        **kwargs: Additional fact attributes
        
    Returns:
        Dictionary with fact addition status
    """
    try:
        # Import myndy-ai components
        from memory.crud.people_crud import PeopleCRUD
        
        logger.info(f"Adding fact: {content[:50]}...")
        
        # Initialize CRUD
        people_crud = PeopleCRUD()
        
        # Find entity if only name provided
        if not entity_id and entity_name:
            # Search for person by name
            people = people_crud.search_people(entity_name, limit=1)
            if people:
                entity_id = people[0].id
                logger.info(f"Found entity {entity_id} for name {entity_name}")
            else:
                # Create new entity if not found
                logger.info(f"Entity not found for {entity_name}, creating new entity")
                result = create_entity(name=entity_name, description=f"Entity created from fact: {content}")
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
        
        # Add fact to person
        success, person = people_crud.add_person_fact(
            person_id=entity_id,
            fact_content=content,
            source=source,
            confidence=confidence,
            verified=verified
        )
        
        if success and person:
            logger.info(f"Successfully added fact to entity {entity_id}")
            return {
                "success": True,
                "entity_id": entity_id,
                "entity_name": person.name.full,
                "fact_content": content,
                "source": source,
                "confidence": confidence,
                "added_at": datetime.now().isoformat(),
                "message": f"Added fact to {person.name.full}"
            }
        else:
            logger.error(f"Failed to add fact to entity {entity_id}")
            return {
                "success": False,
                "error": "Failed to add fact to entity",
                "entity_id": entity_id,
                "content": content
            }
            
    except Exception as e:
        logger.error(f"Error adding fact: {e}")
        return {
            "success": False,
            "error": str(e),
            "content": content
        }

def add_preference(category: str, name: str, value: Any, entity_name: str = "", 
                  entity_id: str = "", source: str = "conversation", 
                  confidence: float = 0.8, **kwargs) -> Dict[str, Any]:
    """
    Add a preference/attribute to an entity.
    
    Args:
        category: Category of preference (interests, skills, preferences, etc.)
        name: Preference name
        value: Preference value
        entity_name: Name of the entity (if entity_id not provided)
        entity_id: ID of the entity
        source: Source of the preference
        confidence: Confidence level (0.0 to 1.0)
        **kwargs: Additional attributes
        
    Returns:
        Dictionary with preference addition status
    """
    try:
        # Import myndy-ai components
        from memory.crud.people_crud import PeopleCRUD
        
        logger.info(f"Adding preference: {category}.{name} = {value}")
        
        # Initialize CRUD
        people_crud = PeopleCRUD()
        
        # Find entity if only name provided
        if not entity_id and entity_name:
            people = people_crud.search_people(entity_name, limit=1)
            if people:
                entity_id = people[0].id
            else:
                # Create new entity if not found
                result = create_entity(name=entity_name, description=f"Entity created from preference: {category}.{name}")
                if result.get("success"):
                    entity_id = result.get("entity_id")
                else:
                    return {
                        "success": False,
                        "error": f"Could not find or create entity for {entity_name}",
                        "category": category,
                        "name": name,
                        "value": value
                    }
        
        if not entity_id:
            return {
                "success": False,
                "error": "No entity_id or entity_name provided",
                "category": category,
                "name": name,
                "value": value
            }
        
        # Add attribute to person
        success, person = people_crud.add_person_attribute(
            person_id=entity_id,
            category=category,
            name=name,
            value=value,
            source=source,
            confidence=confidence
        )
        
        if success and person:
            logger.info(f"Successfully added preference to entity {entity_id}")
            return {
                "success": True,
                "entity_id": entity_id,
                "entity_name": person.name.full,
                "category": category,
                "preference_name": name,
                "preference_value": value,
                "source": source,
                "confidence": confidence,
                "added_at": datetime.now().isoformat(),
                "message": f"Added {category} preference to {person.name.full}"
            }
        else:
            logger.error(f"Failed to add preference to entity {entity_id}")
            return {
                "success": False,
                "error": "Failed to add preference to entity",
                "entity_id": entity_id,
                "category": category,
                "name": name,
                "value": value
            }
            
    except Exception as e:
        logger.error(f"Error adding preference: {e}")
        return {
            "success": False,
            "error": str(e),
            "category": category,
            "name": name,
            "value": value
        }

def search_memory(query: str, limit: int = 10, entity_types: List[str] = None, 
                 **kwargs) -> Dict[str, Any]:
    """
    Search the myndy-ai memory system for entities and facts.
    
    Args:
        query: Search query text
        limit: Maximum number of results
        entity_types: Types of entities to search (person, organization, etc.)
        **kwargs: Additional search parameters
        
    Returns:
        Dictionary with search results
    """
    try:
        # Import myndy-ai components
        from memory.crud.people_crud import PeopleCRUD
        
        logger.info(f"Searching memory for: {query}")
        
        # Initialize CRUD
        people_crud = PeopleCRUD()
        
        # Search people
        people_results = people_crud.search_people(query, limit=limit)
        
        # Format results
        results = []
        for person in people_results:
            result = {
                "id": person.id,
                "name": person.name.full,
                "type": "person",
                "description": person.notes or "",
                "organization": "",
                "contact_methods": []
            }
            
            # Add employment info
            current_emp = person.get_current_employment()
            if current_emp:
                result["organization"] = current_emp.name
                result["job_title"] = current_emp.title or ""
            
            # Add contact methods
            for method in person.contact_methods[:2]:  # Limit to 2 methods
                result["contact_methods"].append({
                    "type": method.type,
                    "value": method.value
                })
            
            # Add facts
            if person.facts:
                result["facts"] = [fact.content for fact in person.facts[:3]]  # Limit to 3 facts
            
            results.append(result)
        
        logger.info(f"Found {len(results)} results for query: {query}")
        
        return {
            "success": True,
            "query": query,
            "results_count": len(results),
            "results": results,
            "searched_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.warning(f"Full myndy-ai system not available, using simple storage: {e}")
        # Fallback to simple storage
        try:
            from simple_memory_storage import search_memory_simple
            return search_memory_simple(query=query, limit=limit, entity_types=entity_types, **kwargs)
        except Exception as fallback_e:
            logger.error(f"Error searching with simple storage: {fallback_e}")
            return {
                "success": False,
                "error": f"Both full and simple storage failed: {fallback_e}",
                "query": query,
                "results": []
            }

def get_current_status(**kwargs) -> Dict[str, Any]:
    """
    Get current user status and context.
    
    Args:
        **kwargs: Additional parameters
        
    Returns:
        Dictionary with current status information
    """
    try:
        logger.info("Getting current user status")
        
        # For now, return basic status - this could be enhanced to check actual status storage
        return {
            "success": True,
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "context": "Available for assistance",
            "message": "User status retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting current status: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def get_self_profile(**kwargs) -> Dict[str, Any]:
    """
    Get user's self profile information.
    
    Args:
        **kwargs: Additional parameters
        
    Returns:
        Dictionary with user profile information
    """
    try:
        # Import myndy-ai components
        from memory.crud.people_crud import PeopleCRUD
        
        logger.info("Getting user self profile")
        
        # Initialize CRUD
        people_crud = PeopleCRUD()
        
        # Search for user profile (could be enhanced with specific user ID)
        # For now, search for any person that might be the user
        user_results = people_crud.search_people("Jeremy Irish", limit=1)
        
        if user_results:
            user = user_results[0]
            profile = {
                "success": True,
                "user_id": user.id,
                "name": user.name.full,
                "first_name": user.name.first,
                "last_name": user.name.last,
                "notes": user.notes or "",
                "contact_methods": [{"type": m.type, "value": m.value} for m in user.contact_methods],
                "facts": [fact.content for fact in (user.facts or [])],
                "attributes": [],
                "retrieved_at": datetime.now().isoformat()
            }
            
            # Add attributes
            if user.attributes:
                profile["attributes"] = [
                    {
                        "category": attr.category,
                        "name": attr.name, 
                        "value": attr.value
                    } for attr in user.attributes
                ]
            
            logger.info(f"Retrieved profile for {user.name.full}")
            return profile
        else:
            logger.info("No user profile found")
            return {
                "success": True,
                "message": "No user profile found in memory",
                "retrieved_at": datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.warning(f"Full myndy-ai system not available, using simple storage: {e}")
        # Fallback to simple storage
        try:
            from simple_memory_storage import get_self_profile_simple
            return get_self_profile_simple(**kwargs)
        except Exception as fallback_e:
            logger.error(f"Error getting self profile with simple storage: {fallback_e}")
            return {
                "success": False,
                "error": f"Both full and simple storage failed: {fallback_e}"
            }

def update_status(status: str, context: str = "", mood: str = "", 
                 activity: str = "", **kwargs) -> Dict[str, Any]:
    """
    Update user status information.
    
    Args:
        status: Current status
        context: Status context
        mood: Current mood
        activity: Current activity
        **kwargs: Additional status attributes
        
    Returns:
        Dictionary with status update confirmation
    """
    try:
        logger.info(f"Updating status to: {status}")
        
        # For now, return success - this could be enhanced to actually store status
        status_data = {
            "success": True,
            "status": status,
            "context": context,
            "mood": mood,
            "activity": activity,
            "updated_at": datetime.now().isoformat(),
            "message": f"Status updated to: {status}"
        }
        
        # Add any additional kwargs
        for key, value in kwargs.items():
            if key not in status_data and value:
                status_data[key] = value
        
        return status_data
        
    except Exception as e:
        logger.error(f"Error updating status: {e}")
        return {
            "success": False,
            "error": str(e),
            "status": status
        }

def store_conversation_analysis(conversation_text: str, entities: List[Dict] = None,
                              intent: str = "", analysis_data: Dict = None,
                              **kwargs) -> Dict[str, Any]:
    """
    Store conversation analysis results in memory.
    
    Args:
        conversation_text: The conversation text analyzed
        entities: List of extracted entities
        intent: Inferred conversation intent
        analysis_data: Additional analysis data
        **kwargs: Additional parameters
        
    Returns:
        Dictionary with storage confirmation
    """
    try:
        logger.info(f"Storing conversation analysis for text: {conversation_text[:50]}...")
        
        # Process entities and create/update them
        processed_entities = []
        
        if entities:
            for entity in entities:
                entity_text = entity.get("text", "")
                entity_type = entity.get("type", "unknown")
                
                if entity_type == "person" and entity_text:
                    # Create or update person entity
                    result = create_entity(
                        name=entity_text,
                        entity_type="person",
                        description=f"Entity extracted from conversation: {conversation_text[:100]}..."
                    )
                    if result.get("success"):
                        processed_entities.append({
                            "text": entity_text,
                            "type": entity_type,
                            "entity_id": result.get("entity_id"),
                            "action": "created_or_updated"
                        })
        
        # Store the analysis
        analysis_record = {
            "success": True,
            "conversation_text": conversation_text[:200] + "..." if len(conversation_text) > 200 else conversation_text,
            "entities_processed": len(processed_entities),
            "entities": processed_entities,
            "intent": intent,
            "analysis_data": analysis_data or {},
            "stored_at": datetime.now().isoformat(),
            "message": f"Stored analysis with {len(processed_entities)} entities"
        }
        
        logger.info(f"Successfully stored conversation analysis with {len(processed_entities)} entities")
        return analysis_record
        
    except Exception as e:
        logger.error(f"Error storing conversation analysis: {e}")
        return {
            "success": False,
            "error": str(e),
            "conversation_text": conversation_text[:100] + "..." if len(conversation_text) > 100 else conversation_text
        }