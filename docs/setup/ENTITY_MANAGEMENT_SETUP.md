# Entity Management System Setup Guide

This guide shows you how to set up a comprehensive entity detection and management system using CrewAI agents with Qdrant vector database.

## 🎯 What This System Does

Your CrewAI agents will automatically:

### **🔍 Detect & Extract:**
- **People** (names, roles, relationships)
- **Organizations** (companies, institutions) 
- **Locations** (cities, addresses, places)
- **Projects** (project names, descriptions)
- **Events** (meetings, deadlines, calendar items)
- **Tasks** (action items, todos)
- **Contacts** (emails, phone numbers)
- **Documents** (files, references)

### **🗄️ Store & Organize:**
- Vector embeddings for semantic search
- Structured metadata for each entity
- Automatic relationship detection
- Duplicate prevention and merging

### **🔎 Search & Analyze:**
- Semantic similarity search
- Trend analysis over time
- Relationship mapping
- Smart recommendations

## 📋 Prerequisites

### 1. Install Required Dependencies

```bash
# Core dependencies
pip install qdrant-client sentence-transformers spacy dateparser phonenumbers geopy

# Install spaCy English model
python -m spacy download en_core_web_sm

# Optional but recommended for better date parsing
pip install dateparser[calendars]
```

### 2. Set Up Qdrant Vector Database

#### Option A: Docker (Recommended)
```bash
# Start Qdrant with Docker
docker run -p 6333:6333 qdrant/qdrant
```

#### Option B: Local Installation
```bash
# Install Qdrant locally
pip install qdrant-client[fastembed]

# Or use Qdrant Cloud (set QDRANT_URL environment variable)
export QDRANT_URL="https://your-cluster.qdrant.tech"
export QDRANT_API_KEY="your-api-key"
```

### 3. Verify Setup

```bash
# Test Qdrant connection
curl http://localhost:6333/health

# Should return: {"status":"ok"}
```

## 🚀 Quick Start

### 1. Basic Entity Extraction

```python
from crewai_entity_agents import create_entity_extraction_workflow

# Your text with entities
text = """
Meeting with John Smith from OpenAI tomorrow at 2 PM in San Francisco.
We're discussing the AI Research Project. Contact: john@openai.com
Action item: Send proposal by Friday.
"""

# Create and run workflow
crew = create_entity_extraction_workflow(text)
result = crew.kickoff()
print(result)
```

### 2. Search for Entities

```python
from crewai_entity_agents import create_entity_search_workflow

# Search for specific entities
crew = create_entity_search_workflow("John Smith", "people")
result = crew.kickoff()
print(result)
```

### 3. Smart Assistant Mode

```python
from crewai_entity_agents import handle_user_request

# Natural language requests
result = handle_user_request("Find all meetings scheduled for next week")
print(result)

result = handle_user_request("Who are all the people from OpenAI in my database?")
print(result)
```

## 🛠️ Recommended Model Configuration

### **For Entity Detection (NER & Pattern Matching):**
```python
llm="ollama/qwen2.5"  # Best reasoning for complex entity detection
```

### **For Database Operations:**
```python  
llm="ollama/codellama"  # Best for API calls and structured operations
```

### **For Analytics & Insights:**
```python
llm="ollama/qwen2.5"  # Superior analytical reasoning
```

### **For General Coordination:**
```python
llm="ollama/llama3.2"  # Good balance for workflow coordination
```

## 📊 Entity Types Supported

| Entity Type | Examples | Collection |
|-------------|----------|------------|
| **People** | "John Smith", "Dr. Sarah Johnson" | `people` |
| **Organizations** | "OpenAI", "Stanford University" | `organizations` |
| **Locations** | "San Francisco", "123 Main St" | `locations` |
| **Projects** | "AI Research Project", "Website Redesign" | `projects` |
| **Events** | "Meeting tomorrow 2 PM", "Deadline Friday" | `events` |
| **Tasks** | "Send proposal", "Review document" | `tasks` |
| **Contacts** | "john@email.com", "(555) 123-4567" | `contacts` |
| **Documents** | "proposal.pdf", "contract.docx" | `documents` |

## 🔧 Advanced Configuration

### Custom Entity Patterns

Add your own entity detection patterns:

```python
# In entity_extraction_tools.py, modify _extract_custom_entities()

custom_patterns = [
    r"budget:?\s*\$([0-9,]+)",  # Budget detection
    r"deadline:?\s+([^.!?\n]{5,30})",  # Deadline detection
    r"client:?\s+([A-Z][a-zA-Z\s]{2,30})",  # Client detection
]
```

### Qdrant Configuration

```python
# Custom Qdrant setup
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(
    url="http://localhost:6333",
    # For Qdrant Cloud:
    # url="https://your-cluster.qdrant.tech",
    # api_key="your-api-key"
)

# Create custom collections
client.create_collection(
    collection_name="custom_entities",
    vectors_config=VectorParams(
        size=384,  # sentence-transformers embedding size
        distance=Distance.COSINE
    )
)
```

### Embedding Model Options

```python
# Different embedding models for different use cases
from sentence_transformers import SentenceTransformer

# Fast and lightweight (default)
embedder = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions

# Better quality, larger size
embedder = SentenceTransformer('all-mpnet-base-v2')  # 768 dimensions

# Multilingual support
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
```

## 📈 Usage Examples

### Example 1: Meeting Notes Processing

```python
meeting_notes = """
Attended quarterly review with:
- Sarah Chen (Product Manager, TechCorp)
- Mike Rodriguez (CTO, DataSoft) 
- Lisa Wang (Director of AI, InnovateLab)

Discussed Q4 roadmap for Machine Learning Platform project.
Budget approved: $250,000

Action items:
- Sarah: Finalize requirements doc by Oct 15
- Mike: Set up development environment by Oct 20  
- Lisa: Prepare ML model evaluation by Oct 25

Next meeting: November 1st, 10 AM PST
Location: TechCorp headquarters, Palo Alto
"""

# Process with CrewAI
crew = create_entity_extraction_workflow(meeting_notes)
result = crew.kickoff()
```

### Example 2: Email Processing

```python
email_text = """
From: john.doe@startup.com
Subject: Partnership Discussion

Hi Sarah,

Following up on our conversation about the AI integration project.
Our team at AI Innovations (555-0123) is excited to collaborate
with DataFlow Systems on this initiative.

Project timeline: 6 months starting January 2024
Budget range: $100K - $150K
Key deliverables: 
- Custom LLM deployment
- API integration  
- Staff training program

Let's schedule a call next week to discuss details.
Available: Tuesday 2-4 PM or Thursday 10 AM-12 PM

Best regards,
John Doe
Senior AI Consultant
john.doe@startup.com
"""

# Extract and store entities
crew = create_entity_extraction_workflow(email_text)
result = crew.kickoff()
```

### Example 3: Project Management

```python
# Search for all tasks related to a project
search_crew = create_entity_search_workflow("Machine Learning Platform", "tasks")
tasks = search_crew.kickoff()

# Find all people involved in AI projects
people_crew = create_entity_search_workflow("AI", "people") 
people = people_crew.kickoff()

# Analyze trends in project creation
from entity_extraction_tools import analyze_entity_trends
trends = analyze_entity_trends("projects", "30d")
```

## 🔍 Search Capabilities

### Semantic Search
```python
# Find entities by meaning, not just keywords
search_entities_in_qdrant("machine learning expert", "people")
search_entities_in_qdrant("tech companies in Silicon Valley", "organizations")
search_entities_in_qdrant("urgent deadlines", "tasks")
```

### Relationship Discovery
```python
# Find related entities
get_entity_relationships("john_smith_123", "people")
# Returns: related projects, organizations, events, etc.
```

### Trend Analysis
```python
# Analyze patterns over time
analyze_entity_trends("events", "7d")   # Meeting frequency
analyze_entity_trends("tasks", "30d")   # Task creation patterns
analyze_entity_trends("people", "90d")  # Contact growth
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Qdrant Connection Failed
```bash
# Check if Qdrant is running
curl http://localhost:6333/health

# Restart Qdrant
docker restart qdrant
```

#### 2. SpaCy Model Missing
```bash
# Install English model
python -m spacy download en_core_web_sm

# Verify installation
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('OK')"
```

#### 3. Memory Issues with Large Texts
```python
# Process in chunks for large documents
def process_large_text(text, chunk_size=1000):
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    for chunk in chunks:
        crew = create_entity_extraction_workflow(chunk)
        crew.kickoff()
```

#### 4. Embedding Model Download Issues
```python
# Pre-download models
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
model.save('local_models/embedder')

# Use local model
embedder = SentenceTransformer('local_models/embedder')
```

## 📊 Performance Optimization

### Hardware Recommendations

| Use Case | RAM | Storage | Notes |
|----------|-----|---------|-------|
| **Development** | 16GB | 10GB | Basic entity extraction |
| **Production (Small)** | 32GB | 50GB | <10K entities/day |
| **Production (Large)** | 64GB+ | 200GB+ | >10K entities/day |

### Optimization Tips

1. **Batch Processing**: Process multiple texts together
2. **Collection Partitioning**: Separate collections by date/type
3. **Index Optimization**: Use appropriate Qdrant configurations
4. **Caching**: Cache embeddings for repeated content

## 🔗 Integration with Existing Projects

Since you have an existing CrewAI project, here's how to integrate the entity management tools:

### 1. **Modular Tool Integration**

Import individual tools into your existing agents:

```python
# Import specific tools you need
from entity_extraction_tools import (
    extract_entities_from_text,
    search_entities_in_qdrant,
    store_entity_in_qdrant,
    get_entity_relationships
)

# Add to your existing agent
your_existing_agent = Agent(
    role="Your Agent Role",
    goal="Your agent goal",
    backstory="Your agent backstory",
    llm="ollama/qwen2.5",
    tools=[
        # Your existing tools
        your_tool_1,
        your_tool_2,
        # Add entity tools
        extract_entities_from_text,
        search_entities_in_qdrant,
    ],
    verbose=True
)
```

### 2. **Standalone Entity Service**

Create a dedicated entity service that your existing agents can call:

```python
# entity_service.py
class EntityService:
    def __init__(self):
        self.extractor = EntityExtractor()
    
    def process_text(self, text: str) -> dict:
        """Process text and return extracted entities"""
        entities = extract_entities_from_text(text)
        return json.loads(entities)
    
    def search(self, query: str, entity_type: str = "all") -> dict:
        """Search for entities"""
        results = search_entities_in_qdrant(query, entity_type)
        return json.loads(results)
    
    def store(self, entity_data: dict, collection: str) -> str:
        """Store entity in database"""
        return store_entity_in_qdrant(json.dumps(entity_data), collection)

# Use in your existing project
entity_service = EntityService()

# In your existing agent tasks
entities = entity_service.process_text(some_text)
search_results = entity_service.search("John Smith", "people")
```

### 3. **Environment Configuration**

Add these environment variables to your existing project:

```bash
# .env file additions
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-api-key-if-using-cloud
EMBEDDING_MODEL=all-MiniLM-L6-v2
SPACY_MODEL=en_core_web_sm

# Optional: Entity extraction settings
ENTITY_CONFIDENCE_THRESHOLD=0.7
DEFAULT_COLLECTION_SIZE=10000
ENABLE_ENTITY_CACHING=true
```

### 4. **Database Schema Integration**

If you have existing databases, bridge them with Qdrant:

```python
# database_bridge.py
class DatabaseBridge:
    def __init__(self, existing_db_conn, qdrant_client):
        self.db = existing_db_conn
        self.qdrant = qdrant_client
    
    def sync_entities_to_qdrant(self):
        """Sync existing database entities to Qdrant"""
        # Get entities from your existing database
        entities = self.db.execute("SELECT * FROM contacts").fetchall()
        
        for entity in entities:
            # Convert to entity format
            entity_data = {
                "text": entity.name,
                "entity_type": "person",
                "metadata": {
                    "id": entity.id,
                    "email": entity.email,
                    "phone": entity.phone,
                    "source": "existing_database"
                }
            }
            
            # Store in Qdrant
            store_entity_in_qdrant(json.dumps(entity_data), "people")
    
    def sync_qdrant_to_db(self):
        """Sync Qdrant entities back to existing database"""
        # Implementation for bi-directional sync
        pass
```

### 5. **API Endpoint Integration**

If your project has APIs, add entity endpoints:

```python
# api_integration.py
from fastapi import FastAPI
from entity_extraction_tools import ENTITY_TOOLS

app = FastAPI()

@app.post("/extract-entities")
async def extract_entities_endpoint(text: str):
    """Extract entities from text via API"""
    result = extract_entities_from_text(text)
    return {"entities": json.loads(result)}

@app.get("/search-entities")
async def search_entities_endpoint(query: str, entity_type: str = "all"):
    """Search entities via API"""
    result = search_entities_in_qdrant(query, entity_type, limit=20)
    return {"results": json.loads(result)}

@app.post("/store-entity")
async def store_entity_endpoint(entity_data: dict, collection: str):
    """Store entity via API"""
    result = store_entity_in_qdrant(json.dumps(entity_data), collection)
    return {"message": result}
```

### 6. **Configuration Manager**

Centralize configuration for easy integration:

```python
# entity_config.py
from dataclasses import dataclass
from typing import Optional, Dict, Any
import os

@dataclass
class EntityConfig:
    """Configuration for entity management system"""
    
    # Qdrant settings
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY")
    
    # Model settings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    spacy_model: str = os.getenv("SPACY_MODEL", "en_core_web_sm")
    
    # Entity extraction settings
    confidence_threshold: float = float(os.getenv("ENTITY_CONFIDENCE_THRESHOLD", "0.7"))
    max_entities_per_text: int = int(os.getenv("MAX_ENTITIES_PER_TEXT", "100"))
    
    # Collections configuration
    collections: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.collections is None:
            self.collections = {
                "people": {"size": 384, "distance": "cosine"},
                "organizations": {"size": 384, "distance": "cosine"},
                "locations": {"size": 384, "distance": "cosine"},
                "projects": {"size": 384, "distance": "cosine"},
                "events": {"size": 384, "distance": "cosine"},
                "tasks": {"size": 384, "distance": "cosine"},
                "contacts": {"size": 384, "distance": "cosine"},
                "documents": {"size": 384, "distance": "cosine"},
            }

# Use in your project
config = EntityConfig()
```

### 7. **Migration Scripts**

Scripts to migrate your existing data:

```python
# migrate_existing_data.py
def migrate_contacts_to_entities():
    """Migrate existing contacts to entity format"""
    # Your existing contact data
    contacts = get_existing_contacts()
    
    for contact in contacts:
        entity_data = {
            "text": contact["name"],
            "entity_type": "person",
            "confidence": 1.0,
            "metadata": {
                "email": contact.get("email"),
                "phone": contact.get("phone"),
                "company": contact.get("company"),
                "migrated_from": "existing_system",
                "original_id": contact["id"]
            }
        }
        
        store_entity_in_qdrant(json.dumps(entity_data), "people")

def migrate_projects_to_entities():
    """Migrate existing projects to entity format"""
    # Implementation for your project data
    pass

# Run migrations
if __name__ == "__main__":
    migrate_contacts_to_entities()
    migrate_projects_to_entities()
    print("Migration completed!")
```

### 8. **Testing Integration**

Test the integration with your existing system:

```python
# test_integration.py
def test_existing_agent_with_entities():
    """Test your existing agent with entity tools"""
    
    # Your existing agent setup
    from your_project import YourExistingAgent
    
    # Add entity tools
    enhanced_agent = YourExistingAgent(
        additional_tools=[extract_entities_from_text, search_entities_in_qdrant]
    )
    
    # Test with sample data
    test_text = "Meeting with John Smith from TechCorp about Project Alpha"
    
    task = Task(
        description=f"Process this text and extract entities: {test_text}",
        agent=enhanced_agent
    )
    
    result = task.execute()
    print("Integration test result:", result)

def test_entity_search_in_existing_workflow():
    """Test entity search within existing workflows"""
    # Your test implementation
    pass
```

### 9. **Monitoring and Logging**

Add monitoring for the entity system:

```python
# entity_monitoring.py
import logging
from datetime import datetime

class EntityMonitor:
    def __init__(self):
        self.logger = logging.getLogger("entity_system")
        
    def log_extraction(self, text_length: int, entities_found: int):
        """Log entity extraction metrics"""
        self.logger.info(f"Extracted {entities_found} entities from {text_length} chars")
    
    def log_search(self, query: str, results_count: int, response_time: float):
        """Log search metrics"""
        self.logger.info(f"Search '{query}' returned {results_count} results in {response_time:.2f}s")
    
    def log_storage(self, entity_type: str, collection: str, success: bool):
        """Log storage operations"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"Storage {status}: {entity_type} to {collection}")

# Use in your tools
monitor = EntityMonitor()
```

### 10. **Gradual Rollout Strategy**

Plan for gradual integration:

```python
# rollout_manager.py
class EntityRolloutManager:
    def __init__(self, config):
        self.config = config
        self.rollout_percentage = config.get("rollout_percentage", 10)
    
    def should_use_entities(self, user_id: str = None) -> bool:
        """Determine if entity system should be used for this request"""
        if self.config.get("force_entities", False):
            return True
        
        # Gradual rollout logic
        import hashlib
        if user_id:
            hash_val = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
            return (hash_val % 100) < self.rollout_percentage
        
        return False

# Use in your existing agents
rollout = EntityRolloutManager(your_config)

if rollout.should_use_entities(user_id):
    # Use entity-enhanced agent
    agent = create_entity_enhanced_agent()
else:
    # Use existing agent
    agent = create_existing_agent()
```

## 🎯 Next Steps

1. **Test the System**: Run the provided examples
2. **Plan Integration**: Choose which integration approach fits your project
3. **Migrate Data**: Run migration scripts for existing data
4. **Customize Patterns**: Add domain-specific entity patterns  
5. **Scale Up**: Configure for your data volume
6. **Monitor**: Set up analytics and monitoring

## 📋 Data Formats and Schemas

### Entity Data Structure

All entities follow this standardized format:

```python
{
    "text": "John Smith",                    # The actual entity text
    "entity_type": "person",             # Type from EntityType enum
    "confidence": 0.95,                  # Confidence score (0.0-1.0)
    "start_pos": 10,                     # Start character position
    "end_pos": 20,                       # End character position
    "metadata": {                        # Additional context
        "context": "Meeting with John Smith tomorrow",
        "source": "email",
        "extracted_at": "2024-01-15T10:30:00Z",
        "relationships": ["project_alpha", "techcorp_org"],
        "custom_fields": {}
    },
    "embedding": [0.1, 0.2, ...],      # Vector embedding (optional)
    "stored_at": "2024-01-15T10:30:00Z", # Storage timestamp
    "updated_at": "2024-01-15T11:00:00Z"  # Last update timestamp
}
```

### Collection Schemas

Each Qdrant collection has specific metadata fields:

```python
# People collection
people_schema = {
    "required_fields": ["text", "entity_type"],
    "optional_fields": {
        "email": "str",
        "phone": "str", 
        "company": "str",
        "role": "str",
        "social_profiles": "dict"
    }
}

# Organizations collection  
organizations_schema = {
    "required_fields": ["text", "entity_type"],
    "optional_fields": {
        "industry": "str",
        "location": "str",
        "website": "str",
        "size": "str",
        "type": "str"  # startup, enterprise, nonprofit, etc.
    }
}

# Projects collection
projects_schema = {
    "required_fields": ["text", "entity_type"],
    "optional_fields": {
        "status": "str",  # active, completed, on-hold
        "priority": "str", # high, medium, low
        "budget": "float",
        "deadline": "datetime",
        "team_members": "list",
        "tags": "list"
    }
}
```

## 🚨 Error Handling and Recovery

### Robust Error Handling

```python
# error_handler.py
from typing import Optional, Dict, Any
import logging

class EntityErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger("entity_errors")
        
    def handle_extraction_error(self, text: str, error: Exception) -> Dict[str, Any]:
        """Handle entity extraction errors gracefully"""
        self.logger.error(f"Extraction failed for text (len={len(text)}): {error}")
        
        return {
            "entities": [],
            "error": str(error),
            "fallback_used": True,
            "extracted_at": datetime.now().isoformat()
        }
    
    def handle_storage_error(self, entity: Dict, error: Exception) -> bool:
        """Handle storage errors with retry logic"""
        self.logger.error(f"Storage failed for entity {entity.get('text', 'unknown')}: {error}")
        
        # Implement retry logic
        for attempt in range(3):
            try:
                # Retry storage operation
                return self._retry_storage(entity)
            except Exception as retry_error:
                self.logger.warning(f"Retry {attempt + 1} failed: {retry_error}")
                
        return False
    
    def handle_search_error(self, query: str, error: Exception) -> Dict[str, Any]:
        """Handle search errors with fallback"""
        self.logger.error(f"Search failed for query '{query}': {error}")
        
        return {
            "results": [],
            "error": str(error),
            "suggested_action": "Check Qdrant connection and try again"
        }

# Use in your tools
error_handler = EntityErrorHandler()

@tool
def robust_extract_entities(text: str) -> str:
    """Extract entities with error handling"""
    try:
        return extract_entities_from_text(text)
    except Exception as e:
        result = error_handler.handle_extraction_error(text, e)
        return json.dumps(result)
```

### Graceful Degradation

```python
# graceful_degradation.py
class EntitySystemFallback:
    def __init__(self):
        self.qdrant_available = self._check_qdrant_health()
        self.spacy_available = self._check_spacy_model()
        
    def extract_with_fallback(self, text: str) -> Dict[str, Any]:
        """Extract entities with multiple fallback methods"""
        
        # Primary: Full NER + patterns + embeddings
        if self.spacy_available and self.qdrant_available:
            return self._full_extraction(text)
            
        # Fallback 1: Regex patterns only
        elif not self.spacy_available:
            return self._regex_only_extraction(text)
            
        # Fallback 2: Local storage only
        elif not self.qdrant_available:
            return self._local_storage_extraction(text)
            
        # Fallback 3: Minimal pattern matching
        else:
            return self._minimal_extraction(text)
```

## 🔐 Security and Privacy

### Data Protection

```python
# security.py
from cryptography.fernet import Fernet
import hashlib

class EntitySecurity:
    def __init__(self, encryption_key: Optional[str] = None):
        self.cipher = Fernet(encryption_key or Fernet.generate_key())
        
    def anonymize_person(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize personal information"""
        if entity.get("entity_type") != "person":
            return entity
            
        # Hash the name for privacy
        name_hash = hashlib.sha256(entity["text"].encode()).hexdigest()[:8]
        
        anonymized = entity.copy()
        anonymized["text"] = f"Person_{name_hash}"
        anonymized["metadata"]["original_name_hash"] = name_hash
        anonymized["metadata"]["anonymized"] = True
        
        # Remove or encrypt sensitive fields
        if "email" in anonymized.get("metadata", {}):
            anonymized["metadata"]["email"] = self._encrypt_field(
                anonymized["metadata"]["email"]
            )
            
        return anonymized
    
    def _encrypt_field(self, value: str) -> str:
        """Encrypt sensitive field values"""
        return self.cipher.encrypt(value.encode()).decode()
    
    def _decrypt_field(self, encrypted_value: str) -> str:
        """Decrypt sensitive field values"""
        return self.cipher.decrypt(encrypted_value.encode()).decode()
```

### Access Control

```python
# access_control.py
from enum import Enum
from typing import Set, Dict

class AccessLevel(Enum):
    READ = "read"
    WRITE = "write" 
    DELETE = "delete"
    ADMIN = "admin"

class EntityAccessControl:
    def __init__(self):
        self.user_permissions: Dict[str, Set[AccessLevel]] = {}
        self.collection_permissions: Dict[str, Set[str]] = {}
    
    def check_access(self, user_id: str, collection: str, action: AccessLevel) -> bool:
        """Check if user has permission for action on collection"""
        user_perms = self.user_permissions.get(user_id, set())
        collection_users = self.collection_permissions.get(collection, set())
        
        return (AccessLevel.ADMIN in user_perms or 
                action in user_perms and user_id in collection_users)
    
    def grant_access(self, user_id: str, collection: str, access_level: AccessLevel):
        """Grant access to user for collection"""
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = set()
        self.user_permissions[user_id].add(access_level)
        
        if collection not in self.collection_permissions:
            self.collection_permissions[collection] = set()
        self.collection_permissions[collection].add(user_id)
```

## 🏭 Production Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Set environment variables
ENV QDRANT_URL=http://qdrant:6333
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "uvicorn", "api_integration:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333

  entity-service:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - qdrant
    environment:
      - QDRANT_URL=http://qdrant:6333
      - EMBEDDING_MODEL=all-MiniLM-L6-v2
    volumes:
      - ./logs:/app/logs

volumes:
  qdrant_data:
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: entity-management
spec:
  replicas: 3
  selector:
    matchLabels:
      app: entity-management
  template:
    metadata:
      labels:
        app: entity-management
    spec:
      containers:
      - name: entity-service
        image: your-registry/entity-management:latest
        ports:
        - containerPort: 8000
        env:
        - name: QDRANT_URL
          value: "http://qdrant-service:6333"
        - name: EMBEDDING_MODEL
          value: "all-MiniLM-L6-v2"
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: entity-management-service
spec:
  selector:
    app: entity-management
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Health Checks and Monitoring

```python
# health_check.py
from typing import Dict, Any
import requests
import time

class HealthChecker:
    def __init__(self, qdrant_url: str):
        self.qdrant_url = qdrant_url
        
    def check_system_health(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        health_status = {
            "timestamp": time.time(),
            "overall_status": "healthy",
            "components": {}
        }
        
        # Check Qdrant
        try:
            response = requests.get(f"{self.qdrant_url}/health", timeout=5)
            health_status["components"]["qdrant"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            health_status["components"]["qdrant"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"
        
        # Check SpaCy model
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            health_status["components"]["spacy"] = {"status": "healthy"}
        except Exception as e:
            health_status["components"]["spacy"] = {
                "status": "unhealthy", 
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"
            
        # Check embedding model
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            health_status["components"]["embeddings"] = {"status": "healthy"}
        except Exception as e:
            health_status["components"]["embeddings"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"
            
        return health_status

# Add to your API
@app.get("/health")
async def health_check():
    checker = HealthChecker(os.getenv("QDRANT_URL"))
    return checker.check_system_health()
```

## 📊 Performance Monitoring

### Metrics Collection

```python
# metrics.py
import time
from typing import Dict, Any
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class EntityMetrics:
    extraction_count: int = 0
    extraction_time: float = 0.0
    storage_count: int = 0
    storage_time: float = 0.0
    search_count: int = 0
    search_time: float = 0.0
    error_count: int = 0

class MetricsCollector:
    def __init__(self):
        self.metrics = defaultdict(EntityMetrics)
        
    def time_operation(self, operation_type: str):
        """Context manager for timing operations"""
        return OperationTimer(self, operation_type)
    
    def record_error(self, error_type: str):
        """Record an error occurrence"""
        self.metrics[error_type].error_count += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        summary = {}
        for key, metrics in self.metrics.items():
            summary[key] = {
                "total_operations": metrics.extraction_count + metrics.storage_count + metrics.search_count,
                "avg_extraction_time": metrics.extraction_time / max(1, metrics.extraction_count),
                "avg_storage_time": metrics.storage_time / max(1, metrics.storage_count),
                "avg_search_time": metrics.search_time / max(1, metrics.search_count),
                "error_rate": metrics.error_count / max(1, metrics.extraction_count + metrics.storage_count + metrics.search_count)
            }
        return summary

class OperationTimer:
    def __init__(self, collector: MetricsCollector, operation_type: str):
        self.collector = collector
        self.operation_type = operation_type
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        metrics = self.collector.metrics[self.operation_type]
        
        if "extraction" in self.operation_type:
            metrics.extraction_count += 1
            metrics.extraction_time += elapsed
        elif "storage" in self.operation_type:
            metrics.storage_count += 1
            metrics.storage_time += elapsed
        elif "search" in self.operation_type:
            metrics.search_count += 1
            metrics.search_time += elapsed

# Use in your tools
metrics = MetricsCollector()

@tool
def monitored_extract_entities(text: str) -> str:
    """Extract entities with performance monitoring"""
    with metrics.time_operation("extraction"):
        try:
            return extract_entities_from_text(text)
        except Exception as e:
            metrics.record_error("extraction_error")
            raise
```

## 📚 Additional Resources

- **Qdrant Documentation**: [qdrant.tech/documentation](https://qdrant.tech/documentation)
- **SpaCy NER Guide**: [spacy.io/usage/linguistic-features#named-entities](https://spacy.io/usage/linguistic-features#named-entities)
- **Sentence Transformers**: [sbert.net](https://sbert.net)
- **CrewAI Tools**: [docs.crewai.com/tools](https://docs.crewai.com/tools)
- **Docker Best Practices**: [docs.docker.com/develop/dev-best-practices](https://docs.docker.com/develop/dev-best-practices)
- **Kubernetes Deployment**: [kubernetes.io/docs/concepts/workloads/deployments](https://kubernetes.io/docs/concepts/workloads/deployments)

---

✅ **Your intelligent entity management system is ready for production!** This comprehensive setup provides everything needed for building robust, scalable information extraction and knowledge management workflows.