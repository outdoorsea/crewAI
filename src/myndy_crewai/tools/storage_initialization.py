"""
Storage Initialization Tool for CrewAI-Myndy Integration

This tool ensures that all necessary storage components are properly initialized
for status and profile persistence, including Qdrant collections and file storage.

File: tools/storage_initialization.py
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Configure logging first
logger = logging.getLogger(__name__)

# Add parent directory to path for config imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.env_config import env_config

# Setup Myndy-AI path from environment
myndy_available = env_config.setup_myndy_path()

if myndy_available:
    # Try to import memory models first (these should work)
    try:
        from memory.status_model import Status
        from memory.self_profile_model import SelfProfile
        memory_models_available = True
        logger.debug("Successfully imported myndy memory model components")
    except ImportError as e:
        logger.warning(f"Could not import myndy memory model components: {e}")
        memory_models_available = False
        Status = None
        SelfProfile = None
    
    # Try to import qdrant components separately (these may fail)
    try:
        from qdrant.collections.memory import memory_manager
        from qdrant.core.client import qdrant_client
        from qdrant.core.collection_manager import collection_manager
        qdrant_available = True
        logger.debug("Successfully imported qdrant components")
    except ImportError as e:
        logger.warning(f"Could not import qdrant components: {e}")
        qdrant_available = False
        memory_manager = None
        qdrant_client = None
        collection_manager = None
else:
    logger.warning(f"Myndy-AI path not found: {env_config.myndy_path}")
    memory_models_available = False
    qdrant_available = False
    memory_manager = None
    Status = None
    SelfProfile = None
    qdrant_client = None
    collection_manager = None

class StorageInitializationTool:
    """Tool for initializing and verifying storage components."""
    
    def __init__(self):
        """Initialize the storage initialization tool."""
        try:
            self.memory_manager = memory_manager  # Use new qdrant architecture directly
            logger.info("Successfully initialized storage components with qdrant")
        except Exception as e:
            logger.error(f"Failed to initialize storage components: {e}")
            self.memory_manager = None
    
    def initialize_all_storage(self) -> Dict[str, Any]:
        """
        Initialize all storage components for status and profile persistence.
        
        Returns:
            Initialization results and status
        """
        try:
            results = {
                "success": True,
                "components_initialized": [],
                "errors": [],
                "collections_created": [],
                "verification_results": {}
            }
            
            # Initialize Qdrant collections
            qdrant_result = self._initialize_qdrant_collections()
            results["qdrant_initialization"] = qdrant_result
            if qdrant_result.get("success"):
                results["components_initialized"].append("qdrant_collections")
                results["collections_created"].extend(qdrant_result.get("collections_created", []))
            else:
                results["errors"].append(f"Qdrant initialization failed: {qdrant_result.get('error')}")
            
            # Initialize memory manager components
            memory_result = self._initialize_memory_manager()
            results["memory_manager_initialization"] = memory_result
            if memory_result.get("success"):
                results["components_initialized"].append("memory_manager")
            else:
                results["errors"].append(f"Memory manager initialization failed: {memory_result.get('error')}")
            
            # Initialize CRUD operations
            crud_result = self._initialize_crud_operations()
            results["crud_initialization"] = crud_result
            if crud_result.get("success"):
                results["components_initialized"].append("crud_operations")
            else:
                results["errors"].append(f"CRUD initialization failed: {crud_result.get('error')}")
            
            # Verify storage functionality
            verification_result = self._verify_storage_functionality()
            results["verification_results"] = verification_result
            
            # Set overall success status
            results["success"] = len(results["errors"]) == 0
            
            return results
            
        except Exception as e:
            logger.error(f"Error initializing storage: {e}")
            return {
                "success": False,
                "error": str(e),
                "components_initialized": [],
                "errors": [str(e)]
            }
    
    def _initialize_qdrant_collections(self) -> Dict[str, Any]:
        """Initialize Qdrant collections for status and profile data."""
        try:
            # Check Qdrant availability
            health_check = qdrant_client.healthcheck()
            if not health_check.get("connected"):
                return {
                    "success": False,
                    "error": "Qdrant server not available",
                    "health_check": health_check
                }
            
            collections_created = []
            required_collections = [
                ("status", 768),
                ("self_profile", 768),
                ("conversation", 768),
                ("entity", 768),
                ("insight", 768),
                ("status_update", 768),
                ("profile_update", 768)
            ]
            
            for collection_name, vector_size in required_collections:
                try:
                    # Get full collection name using collection manager
                    full_collection_name = collection_manager.get_collection_name(collection_name, "memory")
                    
                    # Create collection if it doesn't exist
                    if not qdrant_client.collection_exists(full_collection_name):
                        success = qdrant_client.create_collection(full_collection_name, vector_size)
                        if success:
                            collections_created.append(full_collection_name)
                            logger.info(f"Created collection: {full_collection_name}")
                        else:
                            logger.error(f"Failed to create collection: {full_collection_name}")
                    else:
                        logger.info(f"Collection already exists: {full_collection_name}")
                        
                except Exception as e:
                    logger.error(f"Error creating collection {collection_name}: {e}")
            
            return {
                "success": True,
                "collections_created": collections_created,
                "total_collections_checked": len(required_collections),
                "qdrant_health": health_check
            }
            
        except Exception as e:
            logger.error(f"Error initializing Qdrant collections: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _initialize_memory_manager(self) -> Dict[str, Any]:
        """Initialize memory manager components."""
        try:
            if not self.memory_manager:
                return {
                    "success": False,
                    "error": "Memory manager not available"
                }
            
            # Register model types
            model_registrations = []
            
            # Register Status model
            if 'status' not in self.memory_manager.model_classes:
                self.memory_manager.register_model_type('status', Status)
                model_registrations.append('status')
            
            # Register SelfProfile model
            if 'self_profile' not in self.memory_manager.model_classes:
                self.memory_manager.register_model_type('self_profile', SelfProfile)
                model_registrations.append('self_profile')
            
            return {
                "success": True,
                "model_registrations": model_registrations,
                "registered_models": list(self.memory_manager.model_classes.keys())
            }
            
        except Exception as e:
            logger.error(f"Error initializing memory manager: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _initialize_crud_operations(self) -> Dict[str, Any]:
        """Initialize CRUD operation components."""
        try:
            crud_components = {
                "status_crud": self.status_crud is not None,
                "self_crud": self.self_crud is not None
            }
            
            if self.status_crud:
                # Ensure Status model is registered
                if 'status' not in self.status_crud.memory_manager.model_classes:
                    self.status_crud.memory_manager.register_model_type('status', Status)
            
            if self.self_crud:
                # Ensure SelfProfile model is registered
                if 'self_profile' not in self.self_crud.memory_manager.model_classes:
                    self.self_crud.memory_manager.register_model_type('self_profile', SelfProfile)
            
            return {
                "success": True,
                "crud_components": crud_components,
                "all_components_available": all(crud_components.values())
            }
            
        except Exception as e:
            logger.error(f"Error initializing CRUD operations: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _verify_storage_functionality(self) -> Dict[str, Any]:
        """Verify that storage functionality is working properly."""
        try:
            verification_results = {
                "status_crud_test": False,
                "profile_crud_test": False,
                "qdrant_connectivity": False,
                "memory_manager_test": False
            }
            
            # Test Qdrant connectivity
            try:
                health_check = qdrant_client.healthcheck()
                verification_results["qdrant_connectivity"] = health_check.get("connected", False)
            except Exception as e:
                logger.error(f"Qdrant connectivity test failed: {e}")
            
            # Test memory manager
            if self.memory_manager:
                try:
                    # Simple test of memory manager functionality
                    model_classes = self.memory_manager.model_classes
                    verification_results["memory_manager_test"] = len(model_classes) > 0
                except Exception as e:
                    logger.error(f"Memory manager test failed: {e}")
            
            # Test Status CRUD operations
            if self.status_crud:
                try:
                    # Test getting latest status (should not fail even if no data)
                    latest_status = self.status_crud.get_latest_status("test_user")
                    verification_results["status_crud_test"] = True
                except Exception as e:
                    logger.error(f"Status CRUD test failed: {e}")
            
            # Test Profile CRUD operations
            if self.self_crud:
                try:
                    # Test getting profile (should not fail even if no data)
                    profile = self.self_crud.get_self_profile()
                    verification_results["profile_crud_test"] = True
                except Exception as e:
                    logger.error(f"Profile CRUD test failed: {e}")
            
            return {
                "success": True,
                "verification_results": verification_results,
                "all_tests_passed": all(verification_results.values()),
                "passed_tests": sum(verification_results.values()),
                "total_tests": len(verification_results)
            }
            
        except Exception as e:
            logger.error(f"Error verifying storage functionality: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_storage_status(self) -> Dict[str, Any]:
        """
        Get current status of all storage components.
        
        Returns:
            Current status of storage components
        """
        try:
            status = {
                "memory_manager_available": self.memory_manager is not None,
                "status_crud_available": self.status_crud is not None,
                "self_crud_available": self.self_crud is not None,
                "qdrant_health": {},
                "registered_models": [],
                "collections_status": {}
            }
            
            # Get Qdrant health
            try:
                status["qdrant_health"] = qdrant_client.healthcheck()
            except Exception as e:
                status["qdrant_health"] = {"error": str(e)}
            
            # Get registered models
            if self.memory_manager:
                status["registered_models"] = list(self.memory_manager.model_classes.keys())
            
            # Check collection status
            if status["qdrant_health"].get("connected"):
                collections_to_check = [
                    "status", "self_profile", "conversation", 
                    "entity", "insight", "status_update", "profile_update"
                ]
                
                for collection_name in collections_to_check:
                    try:
                        full_name = collection_manager.get_collection_name(collection_name, "memory")
                        exists = qdrant_client.collection_exists(full_name)
                        count = qdrant_client.count(full_name) if exists else 0
                        status["collections_status"][collection_name] = {
                            "exists": exists,
                            "count": count,
                            "full_name": full_name
                        }
                    except Exception as e:
                        status["collections_status"][collection_name] = {"error": str(e)}
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting storage status: {e}")
            return {"error": str(e)}
    
    def reset_storage(self, confirm: bool = False) -> Dict[str, Any]:
        """
        Reset storage components (use with caution).
        
        Args:
            confirm: Must be True to actually perform reset
            
        Returns:
            Reset operation results
        """
        if not confirm:
            return {
                "success": False,
                "error": "Reset not confirmed. Set confirm=True to proceed with reset."
            }
        
        try:
            reset_results = {
                "collections_deleted": [],
                "errors": []
            }
            
            # Delete collections
            collections_to_reset = [
                "status", "self_profile", "conversation", 
                "entity", "insight", "status_update", "profile_update"
            ]
            
            for collection_name in collections_to_reset:
                try:
                    full_name = collection_manager.get_collection_name(collection_name, "memory")
                    if qdrant_client.collection_exists(full_name):
                        success = qdrant_client.delete_collection(full_name)
                        if success:
                            reset_results["collections_deleted"].append(full_name)
                        else:
                            reset_results["errors"].append(f"Failed to delete collection: {full_name}")
                except Exception as e:
                    reset_results["errors"].append(f"Error deleting collection {collection_name}: {str(e)}")
            
            # Re-initialize after reset
            init_result = self.initialize_all_storage()
            
            return {
                "success": len(reset_results["errors"]) == 0,
                "reset_results": reset_results,
                "reinitialization_results": init_result
            }
            
        except Exception as e:
            logger.error(f"Error resetting storage: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
_storage_tool = StorageInitializationTool()

# Tool functions for registry
def initialize_all_storage() -> str:
    """Initialize all storage components for status and profile persistence."""
    result = _storage_tool.initialize_all_storage()
    return json.dumps(result, indent=2)

def get_storage_status() -> str:
    """Get current status of all storage components."""
    result = _storage_tool.get_storage_status()
    return json.dumps(result, indent=2)

def verify_storage_functionality() -> str:
    """Verify that storage functionality is working properly."""
    result = _storage_tool._verify_storage_functionality()
    return json.dumps(result, indent=2)

def reset_storage(confirm: bool = False) -> str:
    """Reset storage components (use with caution)."""
    result = _storage_tool.reset_storage(confirm)
    return json.dumps(result, indent=2)