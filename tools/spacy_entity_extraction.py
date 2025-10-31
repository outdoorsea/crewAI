"""
SpaCy Entity Extraction Tool for CrewAI Agents

This module provides advanced entity extraction using SpaCy NLP models
for conversation analysis and entity identification.
"""

import spacy
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from langchain.tools import tool

logger = logging.getLogger(__name__)

class SpacyEntityExtractor:
    """SpaCy-based entity extraction with Myndy-AI integration"""
    
    def __init__(self):
        """Initialize SpaCy model and Myndy-AI client"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ SpaCy model 'en_core_web_sm' loaded successfully")
        except OSError:
            logger.error("❌ SpaCy model 'en_core_web_sm' not found. Please install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Myndy-AI API configuration
        self.myndy_api_base = "http://localhost:8000"
        self.api_timeout = 30
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text using SpaCy NLP
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing extracted entities and metadata
        """
        if not self.nlp:
            return {"error": "SpaCy model not available", "entities": []}
        
        try:
            # Process text with SpaCy
            doc = self.nlp(text)
            
            entities = []
            for ent in doc.ents:
                entity_data = {
                    "text": ent.text,
                    "label": ent.label_,
                    "label_description": spacy.explain(ent.label_),
                    "start_char": ent.start_char,
                    "end_char": ent.end_char,
                    "confidence": 0.95  # Default confidence for SpaCy entities
                }
                entities.append(entity_data)
            
            # Extract additional linguistic features
            tokens = []
            for token in doc:
                if not token.is_stop and not token.is_punct and len(token.text.strip()) > 1:
                    token_data = {
                        "text": token.text,
                        "lemma": token.lemma_,
                        "pos": token.pos_,
                        "tag": token.tag_,
                        "is_alpha": token.is_alpha,
                        "is_digit": token.is_digit
                    }
                    tokens.append(token_data)
            
            return {
                "entities_found": len(entities),
                "entities": entities,
                "tokens": tokens,
                "language": doc.lang_,
                "processed_at": datetime.now().isoformat(),
                "original_text": text,
                "text_length": len(text),
                "tool": "spacy_en_core_web_sm"
            }
            
        except Exception as e:
            logger.error(f"Error in SpaCy entity extraction: {e}")
            return {
                "error": str(e),
                "entities": [],
                "processed_at": datetime.now().isoformat()
            }
    
    def categorize_entities(self, entities: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize entities by type for better organization
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Dictionary with entities categorized by type
        """
        categories = {
            "people": [],
            "organizations": [],
            "locations": [],
            "dates": [],
            "times": [],
            "money": [],
            "miscellaneous": []
        }
        
        for entity in entities:
            label = entity.get("label", "")
            
            if label in ["PERSON"]:
                categories["people"].append(entity)
            elif label in ["ORG"]:
                categories["organizations"].append(entity)
            elif label in ["GPE", "LOC", "FAC"]:
                categories["locations"].append(entity)
            elif label in ["DATE"]:
                categories["dates"].append(entity)
            elif label in ["TIME"]:
                categories["times"].append(entity)
            elif label in ["MONEY"]:
                categories["money"].append(entity)
            else:
                categories["miscellaneous"].append(entity)
        
        return categories
    
    def store_entities_in_myndy(self, entities: List[Dict], context: str = "") -> Dict[str, Any]:
        """
        Store extracted entities in Myndy-AI database via API
        
        Args:
            entities: List of extracted entities
            context: Context or source of the entities
            
        Returns:
            API response or error information
        """
        try:
            # Prepare data for Myndy-AI API
            payload = {
                "entities": entities,
                "context": context,
                "extracted_at": datetime.now().isoformat(),
                "extraction_method": "spacy_nlp"
            }
            
            response = requests.post(
                f"{self.myndy_api_base}/api/v1/memory/entities/bulk-store",
                json=payload,
                timeout=self.api_timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "stored_entities": len(entities),
                    "response": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error {response.status_code}: {response.text}",
                    "fallback_storage": "entities not stored"
                }
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to store entities in Myndy-AI: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_storage": "entities not stored - API unavailable"
            }

# Global extractor instance
spacy_extractor = SpacyEntityExtractor()

@tool
def extract_entities_with_spacy(text: str) -> str:
    """
    Extract named entities from text using SpaCy NLP models.
    
    Use this tool when you need to:
    - Extract people, organizations, locations, dates, times from conversation text
    - Perform advanced NLP analysis on user messages
    - Identify specific entities for storage and memory
    
    Parameters:
    - text: The text to analyze (conversation, message, document content)
    
    Returns detailed entity information including entity types, positions, and confidence scores.
    """
    result = spacy_extractor.extract_entities(text)
    return json.dumps(result, indent=2)

@tool
def extract_and_categorize_entities(text: str) -> str:
    """
    Extract entities from text and organize them by category (people, places, dates, etc.).
    
    Use this tool when you need:
    - Organized entity extraction by type
    - Contact management from conversations
    - Event planning with dates/times/locations
    - Structured entity analysis
    
    Parameters:
    - text: The text to analyze and categorize
    
    Returns entities organized by categories: people, organizations, locations, dates, times, money, etc.
    """
    # Extract entities first
    extraction_result = spacy_extractor.extract_entities(text)
    
    if "error" in extraction_result:
        return json.dumps(extraction_result, indent=2)
    
    # Categorize the entities
    entities = extraction_result.get("entities", [])
    categorized = spacy_extractor.categorize_entities(entities)
    
    # Combine with original extraction data
    result = {
        "categorized_entities": categorized,
        "summary": {
            "total_entities": extraction_result["entities_found"],
            "people_found": len(categorized["people"]),
            "organizations_found": len(categorized["organizations"]),
            "locations_found": len(categorized["locations"]),
            "dates_found": len(categorized["dates"]),
            "times_found": len(categorized["times"])
        },
        "metadata": {
            "processed_at": extraction_result["processed_at"],
            "tool": extraction_result["tool"],
            "original_text": extraction_result["original_text"]
        }
    }
    
    return json.dumps(result, indent=2)

@tool  
def extract_and_store_entities(text: str, context: str = "conversation") -> str:
    """
    Extract entities from text using SpaCy and store them in Myndy-AI database.
    
    Use this tool when you need to:
    - Extract AND persist entities for long-term memory
    - Build contact databases from conversations
    - Store important information for future reference
    - Create persistent entity relationships
    
    Parameters:
    - text: The text to analyze
    - context: Context description (e.g., "phone_call", "email", "meeting_notes")
    
    Returns extraction results and storage confirmation.
    """
    # Extract entities
    extraction_result = spacy_extractor.extract_entities(text)
    
    if "error" in extraction_result:
        return json.dumps(extraction_result, indent=2)
    
    entities = extraction_result.get("entities", [])
    
    # Attempt to store in Myndy-AI database
    storage_result = spacy_extractor.store_entities_in_myndy(entities, context)
    
    # Combine results
    result = {
        "extraction": {
            "entities_found": extraction_result["entities_found"],
            "entities": entities
        },
        "storage": storage_result,
        "context": context,
        "processed_at": extraction_result["processed_at"]
    }
    
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    # Test the SpaCy entity extraction
    test_text = "John Smith called about scheduling an appointment with Dr. Jones on Tuesday at 2pm. He can be reached at john@example.com or 555-123-4567."
    
    print("🧪 Testing SpaCy Entity Extraction")
    print("=" * 50)
    
    extractor = SpacyEntityExtractor()
    result = extractor.extract_entities(test_text)
    
    print(f"Text: {test_text}")
    print(f"Entities found: {result.get('entities_found', 0)}")
    
    for entity in result.get('entities', []):
        print(f"  - {entity['text']} ({entity['label']}: {entity['label_description']})")