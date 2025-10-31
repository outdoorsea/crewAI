"""
Comprehensive Memory Storage for All Myndy Models
Provides storage for contacts, emails, events, groups, health, journal, movies, places, projects, tasks, etc.

File: tools/comprehensive_memory_storage.py
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Storage directory for all models
STORAGE_DIR = Path(__file__).parent / "memory_storage"
STORAGE_DIR.mkdir(exist_ok=True)

# Storage files for each model type
STORAGE_FILES = {
    "contacts": STORAGE_DIR / "contacts.json",
    "emails": STORAGE_DIR / "emails.json", 
    "events": STORAGE_DIR / "events.json",
    "groups": STORAGE_DIR / "groups.json",
    "health": STORAGE_DIR / "health.json",
    "journal": STORAGE_DIR / "journal.json",
    "movies": STORAGE_DIR / "movies.json",
    "places": STORAGE_DIR / "places.json",
    "projects": STORAGE_DIR / "projects.json",
    "tasks": STORAGE_DIR / "tasks.json",
    "things": STORAGE_DIR / "things.json",
    "short_term": STORAGE_DIR / "short_term.json"
}

def load_model_storage(model_type: str) -> Dict[str, Any]:
    """Load data from model storage file"""
    try:
        file_path = STORAGE_FILES.get(model_type)
        if file_path and file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading {model_type} storage: {e}")
        return {}

def save_model_storage(model_type: str, data: Dict[str, Any]) -> bool:
    """Save data to model storage file"""
    try:
        file_path = STORAGE_FILES.get(model_type)
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        return False
    except Exception as e:
        logger.error(f"Error saving {model_type} storage: {e}")
        return False

# =================== CONTACT MANAGEMENT ===================

def create_contact(name: str, email: str = "", phone: str = "", address: str = "", 
                  organization: str = "", title: str = "", notes: str = "", **kwargs) -> Dict[str, Any]:
    """Create a new contact"""
    try:
        logger.info(f"Creating contact: {name}")
        
        contacts = load_model_storage("contacts")
        contact_id = f"contact_{uuid.uuid4()}"
        
        # Parse name
        name_parts = name.strip().split()
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        contact_data = {
            "id": contact_id,
            "name": {
                "full": name,
                "first": first_name,
                "last": last_name
            },
            "contact_methods": [],
            "organization": organization,
            "title": title,
            "address": address,
            "notes": notes,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Add contact methods
        if email:
            contact_data["contact_methods"].append({
                "type": "email",
                "value": email,
                "is_primary": True
            })
        if phone:
            contact_data["contact_methods"].append({
                "type": "phone", 
                "value": phone,
                "is_primary": not bool(email)
            })
        
        contacts[contact_id] = contact_data
        
        if save_model_storage("contacts", contacts):
            return {
                "success": True,
                "contact_id": contact_id,
                "name": name,
                "email": email,
                "phone": phone,
                "organization": organization,
                "message": f"Created contact for {name}"
            }
        
        return {"success": False, "error": "Failed to save contact", "name": name}
        
    except Exception as e:
        logger.error(f"Error creating contact {name}: {e}")
        return {"success": False, "error": str(e), "name": name}

# =================== EVENT MANAGEMENT ===================

def create_event(name: str, date: str = "", location: str = "", description: str = "",
                category: str = "event", people: List[str] = None, **kwargs) -> Dict[str, Any]:
    """Create a new event"""
    try:
        logger.info(f"Creating event: {name}")
        
        events = load_model_storage("events")
        event_id = f"event_{uuid.uuid4()}"
        
        event_data = {
            "id": event_id,
            "name": name,
            "date": date,
            "location": location,
            "description": description,
            "category": category,
            "associated_people": people or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        events[event_id] = event_data
        
        if save_model_storage("events", events):
            return {
                "success": True,
                "event_id": event_id,
                "name": name,
                "date": date,
                "location": location,
                "category": category,
                "message": f"Created event: {name}"
            }
            
        return {"success": False, "error": "Failed to save event", "name": name}
        
    except Exception as e:
        logger.error(f"Error creating event {name}: {e}")
        return {"success": False, "error": str(e), "name": name}

# =================== TASK MANAGEMENT ===================

def create_task(title: str, description: str = "", due_date: str = "", status: str = "pending",
               assigned_to: str = "", project: str = "", priority: int = 3, **kwargs) -> Dict[str, Any]:
    """Create a new task"""
    try:
        logger.info(f"Creating task: {title}")
        
        tasks = load_model_storage("tasks")
        task_id = f"task_{uuid.uuid4()}"
        
        task_data = {
            "id": task_id,
            "title": title,
            "description": description,
            "status": status,
            "due_date": due_date,
            "assigned_to": assigned_to,
            "related_project": project,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        tasks[task_id] = task_data
        
        if save_model_storage("tasks", tasks):
            return {
                "success": True,
                "task_id": task_id,
                "title": title,
                "status": status,
                "due_date": due_date,
                "priority": priority,
                "message": f"Created task: {title}"
            }
            
        return {"success": False, "error": "Failed to save task", "title": title}
        
    except Exception as e:
        logger.error(f"Error creating task {title}: {e}")
        return {"success": False, "error": str(e), "title": title}

# =================== PROJECT MANAGEMENT ===================

def create_project(name: str, description: str = "", status: str = "active", 
                  start_date: str = "", end_date: str = "", **kwargs) -> Dict[str, Any]:
    """Create a new project"""
    try:
        logger.info(f"Creating project: {name}")
        
        projects = load_model_storage("projects")
        project_id = f"project_{uuid.uuid4()}"
        
        project_data = {
            "id": project_id,
            "name": name,
            "description": description,
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
            "tasks": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        projects[project_id] = project_data
        
        if save_model_storage("projects", projects):
            return {
                "success": True,
                "project_id": project_id,
                "name": name,
                "status": status,
                "start_date": start_date,
                "message": f"Created project: {name}"
            }
            
        return {"success": False, "error": "Failed to save project", "name": name}
        
    except Exception as e:
        logger.error(f"Error creating project {name}: {e}")
        return {"success": False, "error": str(e), "name": name}

# =================== PLACE MANAGEMENT ===================

def create_place(name: str, address: str = "", city: str = "", country: str = "",
                category: str = "location", description: str = "", **kwargs) -> Dict[str, Any]:
    """Create a new place"""
    try:
        logger.info(f"Creating place: {name}")
        
        places = load_model_storage("places")
        place_id = f"place_{uuid.uuid4()}"
        
        place_data = {
            "id": place_id,
            "name": name,
            "address": address,
            "city": city,
            "country": country,
            "category": category,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        places[place_id] = place_data
        
        if save_model_storage("places", places):
            return {
                "success": True,
                "place_id": place_id,
                "name": name,
                "address": address,
                "city": city,
                "category": category,
                "message": f"Created place: {name}"
            }
            
        return {"success": False, "error": "Failed to save place", "name": name}
        
    except Exception as e:
        logger.error(f"Error creating place {name}: {e}")
        return {"success": False, "error": str(e), "name": name}

# =================== JOURNAL MANAGEMENT ===================

def create_journal_entry(title: str = "", content: str = "", date: str = "", 
                        mood: str = "", tags: List[str] = None, **kwargs) -> Dict[str, Any]:
    """Create a new journal entry"""
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
        logger.info(f"Creating journal entry for {date}")
        
        journal = load_model_storage("journal")
        entry_id = f"journal_{uuid.uuid4()}"
        
        entry_data = {
            "id": entry_id,
            "title": title or f"Journal Entry - {date}",
            "content": content,
            "date": date,
            "mood": mood,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        journal[entry_id] = entry_data
        
        if save_model_storage("journal", journal):
            return {
                "success": True,
                "entry_id": entry_id,
                "title": entry_data["title"],
                "date": date,
                "mood": mood,
                "message": f"Created journal entry for {date}"
            }
            
        return {"success": False, "error": "Failed to save journal entry", "date": date}
        
    except Exception as e:
        logger.error(f"Error creating journal entry: {e}")
        return {"success": False, "error": str(e), "content": content[:50]}

# =================== HEALTH MANAGEMENT ===================

def record_health_data(metric: str, value: str, date: str = "", unit: str = "",
                      notes: str = "", **kwargs) -> Dict[str, Any]:
    """Record health data"""
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
        logger.info(f"Recording health data: {metric} = {value}")
        
        health = load_model_storage("health")
        record_id = f"health_{uuid.uuid4()}"
        
        health_data = {
            "id": record_id,
            "metric": metric,
            "value": value,
            "unit": unit,
            "date": date,
            "notes": notes,
            "created_at": datetime.now().isoformat()
        }
        
        health[record_id] = health_data
        
        if save_model_storage("health", health):
            return {
                "success": True,
                "record_id": record_id,
                "metric": metric,
                "value": value,
                "unit": unit,
                "date": date,
                "message": f"Recorded {metric}: {value} {unit}"
            }
            
        return {"success": False, "error": "Failed to save health data", "metric": metric}
        
    except Exception as e:
        logger.error(f"Error recording health data: {e}")
        return {"success": False, "error": str(e), "metric": metric}

# =================== MOVIE MANAGEMENT ===================

def add_movie(title: str, year: str = "", genre: str = "", rating: str = "", 
             watched: bool = False, notes: str = "", **kwargs) -> Dict[str, Any]:
    """Add a movie to the collection"""
    try:
        logger.info(f"Adding movie: {title}")
        
        movies = load_model_storage("movies")
        movie_id = f"movie_{uuid.uuid4()}"
        
        movie_data = {
            "id": movie_id,
            "title": title,
            "year": year,
            "genre": genre,
            "rating": rating,
            "watched": watched,
            "notes": notes,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        movies[movie_id] = movie_data
        
        if save_model_storage("movies", movies):
            return {
                "success": True,
                "movie_id": movie_id,
                "title": title,
                "year": year,
                "genre": genre,
                "watched": watched,
                "message": f"Added movie: {title}"
            }
            
        return {"success": False, "error": "Failed to save movie", "title": title}
        
    except Exception as e:
        logger.error(f"Error adding movie {title}: {e}")
        return {"success": False, "error": str(e), "title": title}

# =================== GROUP MANAGEMENT ===================

def create_group(name: str, description: str = "", members: List[str] = None,
                category: str = "group", **kwargs) -> Dict[str, Any]:
    """Create a new group"""
    try:
        logger.info(f"Creating group: {name}")
        
        groups = load_model_storage("groups")
        group_id = f"group_{uuid.uuid4()}"
        
        group_data = {
            "id": group_id,
            "name": name,
            "description": description,
            "members": members or [],
            "category": category,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        groups[group_id] = group_data
        
        if save_model_storage("groups", groups):
            return {
                "success": True,
                "group_id": group_id,
                "name": name,
                "members_count": len(members or []),
                "category": category,
                "message": f"Created group: {name}"
            }
            
        return {"success": False, "error": "Failed to save group", "name": name}
        
    except Exception as e:
        logger.error(f"Error creating group {name}: {e}")
        return {"success": False, "error": str(e), "name": name}

# =================== EMAIL MANAGEMENT ===================

def record_email(subject: str, sender: str = "", recipient: str = "", date: str = "",
                summary: str = "", important: bool = False, **kwargs) -> Dict[str, Any]:
    """Record an email"""
    try:
        if not date:
            date = datetime.now().isoformat()
            
        logger.info(f"Recording email: {subject}")
        
        emails = load_model_storage("emails")
        email_id = f"email_{uuid.uuid4()}"
        
        email_data = {
            "id": email_id,
            "subject": subject,
            "sender": sender,
            "recipient": recipient,
            "date": date,
            "summary": summary,
            "important": important,
            "created_at": datetime.now().isoformat()
        }
        
        emails[email_id] = email_data
        
        if save_model_storage("emails", emails):
            return {
                "success": True,
                "email_id": email_id,
                "subject": subject,
                "sender": sender,
                "date": date,
                "important": important,
                "message": f"Recorded email: {subject}"
            }
            
        return {"success": False, "error": "Failed to save email", "subject": subject}
        
    except Exception as e:
        logger.error(f"Error recording email: {e}")
        return {"success": False, "error": str(e), "subject": subject}

# =================== SHORT TERM MEMORY ===================

def add_short_term_memory(content: str, context: str = "", priority: int = 3,
                         expires_at: str = "", **kwargs) -> Dict[str, Any]:
    """Add something to short term memory"""
    try:
        logger.info(f"Adding to short term memory: {content[:50]}...")
        
        short_term = load_model_storage("short_term")
        memory_id = f"shortterm_{uuid.uuid4()}"
        
        memory_data = {
            "id": memory_id,
            "content": content,
            "context": context,
            "priority": priority,
            "expires_at": expires_at,
            "created_at": datetime.now().isoformat()
        }
        
        short_term[memory_id] = memory_data
        
        if save_model_storage("short_term", short_term):
            return {
                "success": True,
                "memory_id": memory_id,
                "content": content[:100],
                "priority": priority,
                "message": "Added to short term memory"
            }
            
        return {"success": False, "error": "Failed to save short term memory", "content": content}
        
    except Exception as e:
        logger.error(f"Error adding short term memory: {e}")
        return {"success": False, "error": str(e), "content": content}

# =================== UNIVERSAL SEARCH ===================

def search_all_memory(query: str, model_types: List[str] = None, limit: int = 10, **kwargs) -> Dict[str, Any]:
    """Search across all memory models"""
    try:
        logger.info(f"Searching all memory for: {query}")
        
        query_lower = query.lower()
        all_results = []
        
        # Define which models to search
        search_models = model_types or list(STORAGE_FILES.keys())
        
        for model_type in search_models:
            try:
                data = load_model_storage(model_type)
                
                for item_id, item in data.items():
                    # Search in various fields based on model type
                    searchable_text = ""
                    
                    if model_type == "contacts":
                        searchable_text = f"{item.get('name', {}).get('full', '')} {item.get('organization', '')} {item.get('notes', '')}"
                    elif model_type == "events":
                        searchable_text = f"{item.get('name', '')} {item.get('location', '')} {item.get('description', '')}"
                    elif model_type == "tasks":
                        searchable_text = f"{item.get('title', '')} {item.get('description', '')}"
                    elif model_type == "projects":
                        searchable_text = f"{item.get('name', '')} {item.get('description', '')}"
                    elif model_type == "places":
                        searchable_text = f"{item.get('name', '')} {item.get('address', '')} {item.get('city', '')}"
                    elif model_type == "journal":
                        searchable_text = f"{item.get('title', '')} {item.get('content', '')}"
                    elif model_type == "health":
                        searchable_text = f"{item.get('metric', '')} {item.get('notes', '')}"
                    elif model_type == "movies":
                        searchable_text = f"{item.get('title', '')} {item.get('genre', '')} {item.get('notes', '')}"
                    elif model_type == "groups":
                        searchable_text = f"{item.get('name', '')} {item.get('description', '')}"
                    elif model_type == "emails":
                        searchable_text = f"{item.get('subject', '')} {item.get('sender', '')} {item.get('summary', '')}"
                    elif model_type == "short_term":
                        searchable_text = f"{item.get('content', '')} {item.get('context', '')}"
                    
                    if query_lower in searchable_text.lower():
                        result = {
                            "id": item_id,
                            "type": model_type,
                            "content": item,
                            "relevance": f"{model_type}_match"
                        }
                        all_results.append(result)
                        
            except Exception as model_e:
                logger.warning(f"Error searching {model_type}: {model_e}")
                continue
        
        # Limit results
        all_results = all_results[:limit]
        
        logger.info(f"Found {len(all_results)} results across all memory types")
        
        return {
            "success": True,
            "query": query,
            "results_count": len(all_results),
            "results": all_results,
            "searched_models": search_models,
            "searched_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error searching all memory: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "results": []
        }