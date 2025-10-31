"""
Pipeline Server for OpenWebUI

Enhanced server with advanced valve management and dynamic configuration
for integration with OpenWebUI.

File: pipeline/server.py
"""

import logging
import sys
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add project paths
PIPELINE_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PIPELINE_ROOT))

from .crewai_myndy_pipeline import Pipeline
from ..api.valve_manager import create_valve_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CrewAI-Myndy Pipeline",
    description="Intelligent agent routing and myndy integration for OpenWebUI with enhanced valve management",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline and valve manager
pipeline = Pipeline()
valve_manager = create_valve_manager(
    pipeline_id=pipeline.id,
    config_path=Path(__file__).parent / f"{pipeline.id}_valves.json"
)

# Configure pipeline with valve manager
pipeline.valve_manager = valve_manager

# Health check endpoint
@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "pipeline": "crewai-myndy",
        "version": "1.0.0",
        "agents_available": len(pipeline.agents)
    }

# Pipeline endpoints for OpenWebUI
@app.get("/models")
async def get_models():
    """Get available models/agents"""
    return {
        "data": pipeline.get_models(),
        "pipelines": True  # This tells OpenWebUI that pipelines are supported
    }

@app.get("/v1/models")
async def get_v1_models():
    """Get available models/agents (OpenAI v1 compatible)"""
    return {
        "data": pipeline.get_models(),
        "pipelines": True  # This tells OpenWebUI that pipelines are supported
    }

@app.get("/manifest")
async def get_manifest():
    """Get pipeline manifest for OpenWebUI"""
    return pipeline.get_manifest()

@app.get("/pipeline")
async def get_pipeline_info():
    """Get pipeline information for OpenWebUI"""
    return {
        "id": pipeline.id,
        "name": pipeline.name,
        "type": pipeline.type,
        "version": pipeline.version,
        "description": "Intelligent agent routing and myndy tool execution",
        "models": pipeline.get_models(),
        "status": "active"
    }

# OpenWebUI Pipeline API endpoints
@app.get("/api/v1/pipelines/list")
async def list_pipelines():
    """List available pipelines for OpenWebUI"""
    return {
        "data": [
            {
                "id": pipeline.id,
                "name": pipeline.name,
                "type": pipeline.type,
                "version": pipeline.version,
                "description": "Intelligent agent routing and myndy tool execution",
                "author": "Jeremy",
                "license": "MIT",
                "status": "active",
                "models": pipeline.get_models()
            }
        ]
    }

@app.get("/api/pipelines")
async def get_pipelines():
    """Get pipelines for OpenWebUI"""
    return {
        "data": [
            {
                "id": pipeline.id,
                "name": pipeline.name,
                "type": pipeline.type,
                "version": pipeline.version,
                "description": "Intelligent agent routing and myndy tool execution",
                "author": "Jeremy",
                "license": "MIT",
                "status": "active"
            }
        ]
    }

@app.get("/pipelines")
async def get_pipelines_root():
    """Get pipelines at root level for OpenWebUI"""
    return {
        "data": [
            {
                "id": pipeline.id,
                "name": pipeline.name,
                "type": pipeline.type,
                "version": pipeline.version,
                "description": "Intelligent agent routing and myndy tool execution",
                "author": "Jeremy",
                "license": "MIT",
                "status": "active",
                "models": pipeline.get_models(),
                "valves": True  # Indicate that this pipeline has configurable valves
            }
        ]
    }

@app.get("/{pipeline_id}/valves/spec")
async def get_valves_spec(pipeline_id: str):
    """Get enhanced pipeline valves specification"""
    if pipeline_id == pipeline.id:
        spec = valve_manager.get_openwebui_spec()
        logger.info(f"🔧 Valve spec requested for pipeline {pipeline_id}")
        return spec
    else:
        raise HTTPException(status_code=404, detail="Pipeline not found")

@app.get("/{pipeline_id}/valves")
async def get_valves(pipeline_id: str):
    """Get current enhanced pipeline valves values"""
    if pipeline_id == pipeline.id:
        values = valve_manager.get_current_values()
        logger.debug(f"🔧 Valve values requested for pipeline {pipeline_id}")
        return values
    else:
        raise HTTPException(status_code=404, detail="Pipeline not found")

@app.post("/{pipeline_id}/valves")
async def update_valves(pipeline_id: str, valves: dict):
    """Update enhanced pipeline valves values with validation"""
    if pipeline_id == pipeline.id:
        try:
            # Update valves with validation
            result = valve_manager.update_values(valves)
            
            # Update pipeline configuration based on valve changes
            _update_pipeline_configuration(result["updated"])
            
            # Log the update
            logger.info(f"🔧 Valves updated for pipeline {pipeline_id}: {list(result['updated'].keys())}")
            
            if result["restart_required"]:
                logger.warning("⚠️ Some valve changes require pipeline restart to take effect")
            
            return {
                "success": True,
                "updated": result["updated"],
                "validation": result["validation"],
                "restart_required": result["restart_required"],
                "current_values": result["current_values"]
            }
            
        except Exception as e:
            logger.error(f"Error updating valves: {e}")
            raise HTTPException(status_code=400, detail=f"Valve update failed: {str(e)}")
    else:
        raise HTTPException(status_code=404, detail="Pipeline not found")

@app.post("/{pipeline_id}/valves/update")
async def update_valves_endpoint(pipeline_id: str, valves: dict):
    """Update pipeline valves values (OpenWebUI compatible endpoint)"""
    return await update_valves(pipeline_id, valves)

def _update_pipeline_configuration(updated_valves: dict):
    """Update pipeline configuration based on valve changes"""
    try:
        # Update pipeline valves object if it exists
        if hasattr(pipeline, 'valves'):
            for key, value in updated_valves.items():
                if hasattr(pipeline.valves, key):
                    setattr(pipeline.valves, key, value)
        
        # Apply specific configuration changes
        if "debug_mode" in updated_valves:
            debug_enabled = updated_valves["debug_mode"]
            if debug_enabled:
                logging.getLogger("crewai").setLevel(logging.DEBUG)
                logging.getLogger("crewai.pipeline").setLevel(logging.DEBUG)
                logger.info("🐛 Debug mode enabled")
            else:
                logging.getLogger("crewai").setLevel(logging.INFO)
                logging.getLogger("crewai.pipeline").setLevel(logging.INFO)
                logger.info("🐛 Debug mode disabled")
        
        if "log_level" in updated_valves:
            log_level = getattr(logging, updated_valves["log_level"].upper(), logging.INFO)
            logging.getLogger("crewai.pipeline").setLevel(log_level)
            logger.info(f"📋 Log level set to {updated_valves['log_level']}")
        
        # Update pipeline router settings if intelligent routing changed
        if "enable_intelligent_routing" in updated_valves and hasattr(pipeline, 'router'):
            pipeline.router.enabled = updated_valves["enable_intelligent_routing"]
            logger.info(f"🧠 Intelligent routing: {'enabled' if updated_valves['enable_intelligent_routing'] else 'disabled'}")
        
        # Update myndy API URL if changed
        if "myndy_api_url" in updated_valves:
            # This would require pipeline restart in most cases
            logger.info(f"🔗 Myndy API URL updated: {updated_valves['myndy_api_url']}")
        
    except Exception as e:
        logger.warning(f"Error applying pipeline configuration changes: {e}")

# Additional valve management endpoints
@app.get("/{pipeline_id}/valves/summary")
async def get_valves_summary(pipeline_id: str):
    """Get valve manager summary"""
    if pipeline_id == pipeline.id:
        summary = valve_manager.get_summary()
        return summary
    else:
        raise HTTPException(status_code=404, detail="Pipeline not found")

@app.get("/{pipeline_id}/valves/export")
async def export_valve_configuration(pipeline_id: str):
    """Export complete valve configuration"""
    if pipeline_id == pipeline.id:
        config = valve_manager.export_configuration()
        return config
    else:
        raise HTTPException(status_code=404, detail="Pipeline not found")

@app.post("/{pipeline_id}/valves/reset")
async def reset_valves(pipeline_id: str):
    """Reset all valves to default values"""
    if pipeline_id == pipeline.id:
        try:
            # Get all default values
            default_values = {}
            for name, valve in valve_manager.valves.items():
                default_values[name] = valve.default_value
            
            # Update with defaults
            result = valve_manager.update_values(default_values)
            _update_pipeline_configuration(result["updated"])
            
            logger.info(f"🔄 All valves reset to defaults for pipeline {pipeline_id}")
            
            return {
                "success": True,
                "message": "All valves reset to default values",
                "current_values": result["current_values"]
            }
            
        except Exception as e:
            logger.error(f"Error resetting valves: {e}")
            raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")
    else:
        raise HTTPException(status_code=404, detail="Pipeline not found")

# Logging and Monitoring Endpoints
@app.get("/{pipeline_id}/logs")
async def get_pipeline_logs(pipeline_id: str, lines: int = 100, level: str = "INFO"):
    """Get recent pipeline logs for debugging and monitoring"""
    if pipeline_id != pipeline.id:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    try:
        import logging
        from io import StringIO
        
        from datetime import datetime
        
        # Check if logs are enabled via valve
        logs_enabled = valve_manager.is_enabled("expose_logs_ui")
        if not logs_enabled:
            return {
                "pipeline_id": pipeline_id,
                "logs": [],
                "message": "Logs are disabled. Enable 'Expose Logs in UI' in pipeline settings.",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get logs from the current log handlers
        logs = []
        
        # Try to read from log files if they exist
        log_files = [
            "/tmp/crewai_pipeline_clean.log",
            "/tmp/crewai_pipeline.log", 
            "/tmp/crewai_pipeline_final.log",
            "/tmp/crewai_pipeline_fixed.log"
        ]
        
        retention_hours = valve_manager.get_value("log_retention_hours", 24)
        cutoff_time = datetime.now().timestamp() - (retention_hours * 3600)
        
        for log_file in log_files:
            try:
                if Path(log_file).exists():
                    with open(log_file, 'r') as f:
                        file_logs = f.readlines()
                        # Get last N lines
                        recent_logs = file_logs[-lines:] if len(file_logs) > lines else file_logs
                        
                        for line in recent_logs:
                            if line.strip():
                                # Parse timestamp from log line if possible
                                try:
                                    if " - " in line and line.startswith("2025-"):
                                        timestamp_str = line.split(" - ")[0]
                                        log_time = datetime.fromisoformat(timestamp_str.replace(",", "."))
                                        
                                        # Skip old logs based on retention
                                        if log_time.timestamp() < cutoff_time:
                                            continue
                                            
                                        # Extract level and message
                                        parts = line.split(" - ", 2)
                                        if len(parts) >= 3:
                                            level_source = parts[1]
                                            message = parts[2].strip()
                                            
                                            # Extract level
                                            if " - " in level_source:
                                                level = level_source.split(" - ")[-1]
                                            else:
                                                level = "INFO"
                                            
                                            logs.append({
                                                "timestamp": log_time.isoformat(),
                                                "level": level,
                                                "source": "pipeline",
                                                "message": message
                                            })
                                        else:
                                            logs.append({
                                                "timestamp": datetime.now().isoformat(),
                                                "level": "INFO",
                                                "source": "pipeline",
                                                "message": line.strip()
                                            })
                                    else:
                                        logs.append({
                                            "timestamp": datetime.now().isoformat(),
                                            "level": "INFO",
                                            "source": "pipeline",
                                            "message": line.strip()
                                        })
                                except Exception:
                                    logs.append({
                                        "timestamp": datetime.now().isoformat(),
                                        "level": "INFO",
                                        "source": "pipeline",
                                        "message": line.strip()
                                    })
                    break  # Use the first available log file
            except Exception as e:
                continue
        
        # Add some recent pipeline status info
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "source": "status",
            "message": f"Pipeline {pipeline_id} is running with {len(pipeline.agents)} agents"
        })
        
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": "INFO", 
            "source": "agents",
            "message": f"Available agents: {list(pipeline.agents.keys())}"
        })
        
        if hasattr(pipeline, 'enhanced_shadow_agent') and pipeline.enhanced_shadow_agent:
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "source": "shadow_agent", 
                "message": "Enhanced Shadow Agent is active and monitoring conversations"
            })
        
        return {
            "pipeline_id": pipeline_id,
            "logs": logs[-lines:],  # Limit to requested number of lines
            "total_lines": len(logs),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")

@app.get("/{pipeline_id}/status")
async def get_pipeline_status(pipeline_id: str):
    """Get detailed pipeline status and metrics"""
    if pipeline_id != pipeline.id:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    try:
        from datetime import datetime
        
        # Get valve settings
        debug_mode = valve_manager.is_enabled("debug_mode")
        log_level = valve_manager.get_value("log_level", "INFO")
        logs_ui_enabled = valve_manager.is_enabled("expose_logs_ui")
        
        status = {
            "pipeline_id": pipeline_id,
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "agents": {
                "total": len(pipeline.agents),
                "available": list(pipeline.agents.keys()),
                "crewai_available": getattr(pipeline, 'crewai_available', False)
            },
            "features": {
                "intelligent_routing": valve_manager.is_enabled("enable_intelligent_routing"),
                "enhanced_shadow_agent": hasattr(pipeline, 'enhanced_shadow_agent') and pipeline.enhanced_shadow_agent is not None,
                "memory_integration": valve_manager.is_enabled("enable_memory_search"),
                "valve_management": True,
                "tool_execution": valve_manager.is_enabled("enable_tool_execution"),
                "contact_management": valve_manager.is_enabled("enable_contact_management")
            },
            "debugging": {
                "debug_mode": debug_mode,
                "log_level": log_level,
                "logs_ui_enabled": logs_ui_enabled,
                "log_agent_decisions": valve_manager.is_enabled("log_agent_decisions")
            },
            "configuration": {
                "max_iter": valve_manager.get_value("max_agent_iterations", 25),
                "max_execution_time": valve_manager.get_value("tool_timeout", 30),
                "verbose_mode": debug_mode,
                "myndy_api_url": valve_manager.get_value("myndy_api_url", "http://localhost:8000"),
                "routing_confidence": valve_manager.get_value("routing_confidence_threshold", 0.7)
            }
        }
        
        # Add valve manager info
        if hasattr(pipeline, 'valve_manager'):
            enabled_features = [name for name, valve in valve_manager.valves.items() 
                              if valve.valve_type.value == "boolean" and valve_manager.is_enabled(name)]
            
            status["valves"] = {
                "total": len(valve_manager.valves),
                "enabled_features": enabled_features,
                "categories": list(valve_manager.categories.keys())
            }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting pipeline status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@app.get("/{pipeline_id}/diagnostics")
async def get_pipeline_diagnostics(pipeline_id: str):
    """Get diagnostic information about pipeline issues and health"""
    if pipeline_id != pipeline.id:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    try:
        from datetime import datetime
        
        diagnostics = {
            "pipeline_id": pipeline_id,
            "timestamp": datetime.now().isoformat(),
            "health_check": {
                "status": "healthy",
                "issues": []
            },
            "recent_errors": [],
            "performance_metrics": {},
            "suggestions": []
        }
        
        # Check for common issues from logs
        error_patterns = [
            ("422 Unprocessable Content", "Enhanced Shadow Agent has validation errors when storing journal entries"),
            ("'AIMessage' object has no attribute 'find'", "LLM response parsing issue in Enhanced Shadow Agent"),
            ("Invalid \\escape", "JSON parsing error in chat completions"),
            ("tool validation", "Agent tool selection issues"),
            ("401 Unauthorized", "API authentication problems with myndy-ai backend")
        ]
        
        # Scan recent logs for errors
        try:
            log_file = "/tmp/crewai_pipeline_clean.log"
            if Path(log_file).exists():
                with open(log_file, 'r') as f:
                    recent_lines = f.readlines()[-50:]  # Last 50 lines
                    
                for line in recent_lines:
                    for pattern, description in error_patterns:
                        if pattern in line:
                            diagnostics["recent_errors"].append({
                                "pattern": pattern,
                                "description": description,
                                "line": line.strip(),
                                "severity": "warning" if "WARNING" in line else "error"
                            })
                            
                            if description not in [issue["description"] for issue in diagnostics["health_check"]["issues"]]:
                                diagnostics["health_check"]["issues"].append({
                                    "type": "error",
                                    "description": description,
                                    "impact": "medium"
                                })
        except Exception as e:
            diagnostics["health_check"]["issues"].append({
                "type": "system",
                "description": f"Could not read log files: {str(e)}",
                "impact": "low"
            })
        
        # Provide suggestions based on detected issues
        if any("Enhanced Shadow Agent" in error["description"] for error in diagnostics["recent_errors"]):
            diagnostics["suggestions"].append({
                "issue": "Enhanced Shadow Agent validation errors",
                "solution": "Fix journal entry schema validation - ensure 'title' field is provided and 'mood' is dict format",
                "priority": "medium"
            })
        
        if any("tool validation" in error["description"] for error in diagnostics["recent_errors"]):
            diagnostics["suggestions"].append({
                "issue": "Agent tool selection problems",
                "solution": "Check tool registration and agent tool mappings in myndy_bridge.py",
                "priority": "high"
            })
        
        if any("401 Unauthorized" in error["description"] for error in diagnostics["recent_errors"]):
            diagnostics["suggestions"].append({
                "issue": "API authentication failures",
                "solution": "Verify API keys and myndy-ai backend authentication configuration",
                "priority": "high"
            })
        
        # Update health status
        if diagnostics["health_check"]["issues"]:
            diagnostics["health_check"]["status"] = "degraded" if len(diagnostics["health_check"]["issues"]) < 3 else "unhealthy"
        
        return diagnostics
        
    except Exception as e:
        logger.error(f"Error getting pipeline diagnostics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get diagnostics: {str(e)}")

async def _handle_chat_completions(request: dict):
    """Handle chat completions logic"""
    try:
        messages = request.get("messages", [])
        model = request.get("model", "auto")
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Process through pipeline
        response = pipeline.pipe(
            user_message=user_message,
            model_id=model,
            messages=messages,
            body=request
        )
        
        # Return OpenAI-compatible response
        return {
            "id": f"chatcmpl-{int(__import__('time').time())}",
            "object": "chat.completion", 
            "created": int(__import__('time').time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(str(response).split()),
                "total_tokens": len(user_message.split()) + len(str(response).split())
            }
        }
        
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        return {
            "error": {
                "message": str(e),
                "type": "pipeline_error"
            }
        }

@app.post("/chat/completions")
async def chat_completions(request: Request):
    """Handle chat completions"""
    body = await request.json()
    return await _handle_chat_completions(body)

@app.post("/v1/chat/completions")
async def v1_chat_completions(request: Request):
    """Handle chat completions (OpenAI v1 compatible)"""
    body = await request.json()
    return await _handle_chat_completions(body)

def main():
    """Run the enhanced pipeline server"""
    logger.info("Starting Enhanced CrewAI-Myndy Pipeline Server v2.0")
    logger.info("🚀 Features: Intelligent Agent Routing + Enhanced Valve Management + Memory Search")
    logger.info(f"🤖 Available agents: {len(pipeline.agents)} specialized agents + auto-routing")
    logger.info(f"🔧 Valve management: {len(valve_manager.valves)} configurable valves in {len(valve_manager.categories)} categories")
    
    # Display valve summary
    summary = valve_manager.get_summary()
    enabled_features = ", ".join(summary.get("enabled_features", []))
    logger.info(f"✅ Enabled features: {enabled_features}")
    
    logger.info("🌐 Server starting on http://localhost:9099")
    logger.info("📋 Add this URL to OpenWebUI Pipelines: http://localhost:9099")
    logger.info("🔧 Valve Management:")
    logger.info("   - Enhanced valve specification with categories and validation")
    logger.info("   - Real-time configuration updates")
    logger.info("   - Advanced options for expert users")
    logger.info("   - Persistent configuration storage")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9099,
        log_level="info"
    )

if __name__ == "__main__":
    main()