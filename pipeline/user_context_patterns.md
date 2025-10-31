# OpenWebUI User Context Integration Patterns

## Overview

This guide shows how to modify your existing Myndy AI pipelines to capture and use user information from OpenWebUI.

## 1. Current vs Enhanced Pipeline Signature

### Current Signature (Legacy)
```python
def pipe(self, user_message: str, model_id: str, messages: List[Dict[str, Any]], body: Dict[str, Any]) -> str:
```

### Enhanced Signature (User-Aware)
```python
async def pipe(
    self,
    body: dict,
    __user__: Optional[Dict[str, Any]] = None,
    __request__: Optional[Any] = None,
    __event_emitter__: Optional[Any] = None,
    __event_call__: Optional[Any] = None,
    __task__: Optional[str] = None,
    __task_body__: Optional[dict] = None,
    __files__: Optional[list] = None,
    __metadata__: Optional[dict] = None,
    __tools__: Optional[dict] = None,
) -> Union[str, Generator, Iterator]:
```

## 2. User Information Structure

### `__user__` Parameter Contains:
```python
{
    "id": "user_123",           # Unique user identifier
    "name": "John Doe",         # User display name
    "email": "john@example.com", # User email (if available)
    "role": "user",             # User role (admin, user, etc.)
    # Additional fields may be available depending on OpenWebUI configuration
}
```

### `__request__` Parameter Provides:
- HTTP headers (including authentication headers)
- Request metadata
- Client information

## 3. Implementation Patterns

### Pattern 1: Basic User Logging
```python
def _log_user_activity(self, __user__):
    if __user__:
        logger.info(f"👤 Request from: {__user__.get('name', 'Unknown')} (ID: {__user__.get('id', 'N/A')})")
    else:
        logger.info("👤 Anonymous request")
```

### Pattern 2: User Session Management
```python
def _get_user_session(self, __user__):
    if not __user__:
        return {"id": "anonymous", "preferences": {}}
    
    user_id = __user__.get("id")
    if user_id not in self.user_sessions:
        self.user_sessions[user_id] = {
            "id": user_id,
            "name": __user__.get("name"),
            "preferences": {},
            "conversation_history": [],
            "session_start": datetime.now().isoformat()
        }
    return self.user_sessions[user_id]
```

### Pattern 3: Header Extraction
```python
def _extract_headers(self, __request__):
    headers = {}
    if __request__ and hasattr(__request__, 'headers'):
        request_headers = dict(__request__.headers)
        # Extract relevant headers
        headers = {
            'user_agent': request_headers.get('user-agent'),
            'client_ip': request_headers.get('x-forwarded-for') or request_headers.get('x-real-ip'),
            'authorization': request_headers.get('authorization'),
            # OpenWebUI-specific headers
            'x_user_id': request_headers.get('x-user-id'),
            'x_user_email': request_headers.get('x-user-email'),
        }
    return {k: v for k, v in headers.items() if v is not None}
```

## 4. Modifying Existing Pipeline Files

### For `openwebui_pipeline.py`:
```python
# Change the pipe function signature
async def pipe(
    self, 
    body: dict,
    __user__: Optional[Dict[str, Any]] = None,
    __request__: Optional[Any] = None
) -> Union[str, Generator, Iterator]:
    
    # Extract user info
    user_info = self._extract_user_info(__user__)
    
    # Log user activity
    if self.valves.enable_user_logging:
        logger.info(f"👤 Processing request for: {user_info['name']}")
    
    # Extract traditional parameters from body for compatibility
    messages = body.get("messages", [])
    model_id = body.get("model", "auto")
    
    user_message = ""
    for message in reversed(messages):
        if message.get("role") == "user":
            user_message = message.get("content", "")
            break
    
    # Call existing pipeline with enhanced context
    enhanced_body = body.copy()
    enhanced_body["__user_context__"] = user_info
    
    # Delegate to existing implementation
    return await self._original_pipe(user_message, model_id, messages, enhanced_body)
```

### For `server_with_logs.py`:
```python
# Update the middleware to log user information
@app.middleware("http")
async def log_requests_with_user(request: Request, call_next):
    start_time = time.time()
    
    # Extract user info from headers if available
    user_id = request.headers.get('x-user-id', 'anonymous')
    user_name = request.headers.get('x-user-name', 'Unknown')
    
    logger.info(f"📥 {request.method} {request.url.path} | User: {user_name} ({user_id})")
    
    response = await call_next(request)
    process_time = time.time() - start_time
    status_emoji = "✅" if response.status_code < 400 else "❌"
    logger.info(f"📤 {status_emoji} {response.status_code} | {process_time:.3f}s | User: {user_name}")
    return response
```

## 5. FastAPI Server Integration

### Enhanced Chat Completions Endpoint:
```python
@app.post("/v1/chat/completions")
async def chat_completions(request: dict, http_request: Request):
    try:
        # Extract user information from headers
        user_info = {
            "id": http_request.headers.get('x-user-id', 'anonymous'),
            "name": http_request.headers.get('x-user-name', 'Unknown User'),
            "email": http_request.headers.get('x-user-email'),
            "role": http_request.headers.get('x-user-role', 'user')
        }
        
        logger.info(f"💬 Chat request from: {user_info['name']} ({user_info['id']})")
        
        # Call pipeline with user context
        response = await pipeline.pipe(
            body=request,
            __user__=user_info,
            __request__=http_request
        )
        
        # Return OpenAI-compatible response with user tracking
        return {
            "id": f"chatcmpl-{datetime.now().timestamp()}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": request.get("model", "auto"),
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(str(request).split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(str(request).split()) + len(response.split())
            },
            "__user_context__": user_info  # Optional: include for debugging
        }
    except Exception as e:
        logger.error(f"❌ Error for user {user_info.get('name', 'Unknown')}: {e}")
        return {"error": {"message": str(e), "type": "pipeline_error", "code": "processing_failed"}}
```

## 6. Configuration for User Context

### Enhanced Valves Configuration:
```python
class Valves(BaseModel):
    # Existing valves
    enable_intelligent_routing: bool = True
    enable_tool_execution: bool = True
    debug_mode: bool = False
    
    # New user-aware valves
    enable_user_tracking: bool = True
    enable_user_logging: bool = True
    store_user_preferences: bool = True
    user_session_timeout: int = 3600  # 1 hour
    max_conversation_history: int = 100
    enable_user_personalization: bool = True
```

## 7. User Personalization Features

### Personalizing Agent Responses:
```python
def _personalize_response(self, response: str, user_info: Dict[str, Any]) -> str:
    # Add user's name to response
    if user_info.get('name') and user_info['name'] != 'Unknown User':
        # Replace generic greetings with personalized ones
        personalized = response.replace(
            "Hello!", 
            f"Hello {user_info['name']}!"
        )
        return personalized
    return response
```

### User Preference Storage:
```python
def _save_user_preference(self, user_id: str, preference_key: str, preference_value: Any):
    if user_id not in self.user_preferences:
        self.user_preferences[user_id] = {}
    self.user_preferences[user_id][preference_key] = preference_value
    
def _get_user_preference(self, user_id: str, preference_key: str, default=None):
    return self.user_preferences.get(user_id, {}).get(preference_key, default)
```

## 8. Testing User Context

### Test Function:
```python
async def test_user_context():
    pipeline = Pipeline()
    
    # Mock user data
    test_user = {
        "id": "test_123",
        "name": "Test User",
        "email": "test@example.com",
        "role": "admin"
    }
    
    test_body = {
        "messages": [{"role": "user", "content": "Hello, can you help me?"}],
        "model": "auto"
    }
    
    # Test the enhanced pipe function
    response = await pipeline.pipe(
        body=test_body,
        __user__=test_user
    )
    
    print(f"Response for {test_user['name']}: {response}")
```

## 9. Security Considerations

### Sanitize User Data:
```python
def _sanitize_user_info(self, __user__):
    if not __user__:
        return None
    
    # Remove sensitive information from logs
    safe_user = {
        "id": __user__.get("id", "unknown"),
        "name": __user__.get("name", "Unknown"),
        "role": __user__.get("role", "user"),
        # Don't log email or other sensitive data
    }
    return safe_user
```

### Validate User Permissions:
```python
def _check_user_permissions(self, __user__, requested_action: str) -> bool:
    if not __user__:
        return False  # Anonymous users have limited access
    
    user_role = __user__.get("role", "user")
    
    # Define role-based permissions
    permissions = {
        "admin": ["all"],
        "user": ["basic_chat", "memory_search", "personal_tools"],
        "guest": ["basic_chat"]
    }
    
    return requested_action in permissions.get(user_role, [])
```

## 10. Migration Strategy

### Backward Compatibility:
```python
def pipe(self, *args, **kwargs):
    # Support both old and new signatures
    if len(args) >= 4:
        # Old signature: pipe(user_message, model_id, messages, body)
        return self._legacy_pipe(*args, **kwargs)
    else:
        # New signature: pipe(body, __user__, __request__, ...)
        return self._enhanced_pipe(*args, **kwargs)
```

This pattern guide provides comprehensive approaches to integrate user context awareness into your existing Myndy AI pipeline architecture while maintaining backward compatibility.