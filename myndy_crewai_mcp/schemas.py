"""
MCP Data Schemas

Data schemas and type definitions for MCP protocol messages,
tools, resources, and prompts.

File: mcp/schemas.py
"""

from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum


# ============================================================================
# MCP Protocol Schemas (JSON-RPC 2.0)
# ============================================================================

class MCPRequest(BaseModel):
    """MCP JSON-RPC request"""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    id: Optional[Union[str, int]] = Field(default=None, description="Request ID")
    method: str = Field(..., description="Method name")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Method parameters")


class MCPResponse(BaseModel):
    """MCP JSON-RPC response"""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    id: Optional[Union[str, int]] = Field(default=None, description="Request ID")
    result: Optional[Any] = Field(default=None, description="Result data")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error information")


class MCPError(BaseModel):
    """MCP error information"""
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Any] = Field(default=None, description="Additional error data")


# ============================================================================
# Tool Schemas
# ============================================================================

class ToolParameterType(str, Enum):
    """Tool parameter types"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class ToolParameter(BaseModel):
    """Tool parameter definition"""
    name: str = Field(..., description="Parameter name")
    type: ToolParameterType = Field(..., description="Parameter type")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(default=False, description="Whether parameter is required")
    default: Optional[Any] = Field(default=None, description="Default value")
    enum: Optional[List[str]] = Field(default=None, description="Allowed values")

    class Config:
        use_enum_values = True


class ToolDefinition(BaseModel):
    """MCP tool definition"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    inputSchema: Dict[str, Any] = Field(
        ...,
        description="JSON Schema for tool parameters"
    )

    @classmethod
    def from_parameters(
        cls,
        name: str,
        description: str,
        parameters: List[ToolParameter]
    ) -> "ToolDefinition":
        """Create tool definition from parameter list"""
        properties = {}
        required = []

        for param in parameters:
            # Handle both enum and string types
            param_type = param.type.value if hasattr(param.type, 'value') else param.type
            properties[param.name] = {
                "type": param_type,
                "description": param.description,
            }
            if param.default is not None:
                properties[param.name]["default"] = param.default
            if param.enum:
                properties[param.name]["enum"] = param.enum
            if param.required:
                required.append(param.name)

        input_schema = {
            "type": "object",
            "properties": properties,
        }
        if required:
            input_schema["required"] = required

        return cls(
            name=name,
            description=description,
            inputSchema=input_schema
        )


class ToolCallRequest(BaseModel):
    """Request to call a tool"""
    name: str = Field(..., description="Tool name")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class ToolCallResult(BaseModel):
    """Result from tool execution"""
    content: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Tool result content"
    )
    isError: bool = Field(default=False, description="Whether an error occurred")


# ============================================================================
# Resource Schemas
# ============================================================================

class ResourceType(str, Enum):
    """Resource types"""
    TEXT = "text"
    JSON = "application/json"
    BINARY = "application/octet-stream"
    HTML = "text/html"
    MARKDOWN = "text/markdown"


class ResourceDefinition(BaseModel):
    """MCP resource definition"""
    uri: str = Field(..., description="Resource URI (e.g., myndy://memory/entities)")
    name: str = Field(..., description="Resource name")
    description: str = Field(..., description="Resource description")
    mimeType: str = Field(
        default="application/json",
        description="Resource MIME type"
    )


class ResourceContent(BaseModel):
    """Resource content"""
    uri: str = Field(..., description="Resource URI")
    mimeType: str = Field(..., description="Content MIME type")
    text: Optional[str] = Field(default=None, description="Text content")
    blob: Optional[str] = Field(default=None, description="Base64-encoded binary content")


class ResourceTemplate(BaseModel):
    """Resource URI template"""
    uriTemplate: str = Field(..., description="URI template with variables")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    mimeType: str = Field(default="application/json", description="Resource MIME type")


# ============================================================================
# Prompt Schemas
# ============================================================================

class PromptArgument(BaseModel):
    """Prompt template argument"""
    name: str = Field(..., description="Argument name")
    description: str = Field(..., description="Argument description")
    required: bool = Field(default=False, description="Whether argument is required")


class PromptMessage(BaseModel):
    """Prompt message"""
    role: Literal["system", "user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")


class PromptDefinition(BaseModel):
    """MCP prompt definition"""
    name: str = Field(..., description="Prompt name")
    description: str = Field(..., description="Prompt description")
    arguments: List[PromptArgument] = Field(
        default_factory=list,
        description="Prompt arguments"
    )


class PromptResult(BaseModel):
    """Result from getting a prompt"""
    description: Optional[str] = Field(default=None, description="Prompt description")
    messages: List[PromptMessage] = Field(..., description="Prompt messages")


# ============================================================================
# Server Info Schemas
# ============================================================================

class ServerCapabilities(BaseModel):
    """Server capabilities"""
    tools: Optional[Dict[str, Any]] = Field(default=None, description="Tools capability")
    resources: Optional[Dict[str, Any]] = Field(default=None, description="Resources capability")
    prompts: Optional[Dict[str, Any]] = Field(default=None, description="Prompts capability")
    logging: Optional[Dict[str, Any]] = Field(default=None, description="Logging capability")


class ServerInfo(BaseModel):
    """Server information"""
    name: str = Field(..., description="Server name")
    version: str = Field(..., description="Server version")
    protocolVersion: str = Field(default="2024-11-05", description="MCP protocol version")
    capabilities: ServerCapabilities = Field(..., description="Server capabilities")


class InitializeResult(BaseModel):
    """Result from initialization"""
    protocolVersion: str = Field(default="2024-11-05", description="MCP protocol version")
    capabilities: ServerCapabilities = Field(..., description="Server capabilities")
    serverInfo: ServerInfo = Field(..., description="Server information")


# ============================================================================
# Utility Functions
# ============================================================================

def create_tool_result(
    content: Any,
    is_error: bool = False,
    content_type: str = "text"
) -> ToolCallResult:
    """Create a tool call result"""
    if isinstance(content, str):
        result_content = [{"type": content_type, "text": content}]
    elif isinstance(content, dict) or isinstance(content, list):
        import json
        result_content = [{"type": "text", "text": json.dumps(content, indent=2)}]
    else:
        result_content = [{"type": "text", "text": str(content)}]

    return ToolCallResult(content=result_content, isError=is_error)


def create_error_result(error_message: str) -> ToolCallResult:
    """Create an error result"""
    return create_tool_result(
        content=f"Error: {error_message}",
        is_error=True
    )


def create_resource_content(
    uri: str,
    content: Union[str, Dict, List],
    mime_type: str = "application/json"
) -> ResourceContent:
    """Create resource content"""
    if isinstance(content, str):
        text_content = content
    else:
        import json
        text_content = json.dumps(content, indent=2)

    return ResourceContent(
        uri=uri,
        mimeType=mime_type,
        text=text_content
    )
