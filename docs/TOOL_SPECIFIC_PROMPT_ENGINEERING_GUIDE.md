# Tool-Specific Prompt Engineering Guide for CrewAI Agents

## Overview

This guide provides specific prompt engineering patterns for CrewAI agents to effectively integrate with the 530+ Myndy-AI FastAPI tools. Each tool category has unique requirements, parameters, and usage patterns that agents must understand for optimal performance.

## 🚀 FastAPI Tool Integration Architecture

### HTTP Client Pattern for All Tools

All CrewAI tools must use HTTP clients to communicate with the Myndy-AI FastAPI backend:

```python
@tool
def tool_name(parameter: str = "default") -> str:
    """Tool description following best practices"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/tools/execute",
            json={
                "tool_name": "backend_tool_name",
                "parameters": {"param": parameter}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Tool execution failed: {str(e)}"
```

### Agent Tool Usage Prompts

#### For Personal Assistant Agents:
```python
"🔧 MYNDY-AI TOOL INTEGRATION:\n"
"• TIME QUERIES → use get_current_time with specific timezone parameters\n"
"• CALENDAR OPERATIONS → use calendar_query with action-specific parameters\n"
"• WEATHER INFORMATION → use local_weather or weather_api with location\n"
"• CONVERSATION ANALYSIS → use extract_conversation_entities for insights\n"
"\n"
"HTTP EXECUTION PATTERN: All tools accessed via POST to /api/v1/tools/execute\n"
"PARAMETER VALIDATION: Always validate required vs optional parameters\n"
"ERROR HANDLING: Implement graceful fallbacks for API failures"
```

## 📊 Tool Category-Specific Prompt Patterns

### 🕐 Time & Date Management Tools

#### **get_current_time**

**Agent Prompt Integration:**
```python
"For TIME QUERIES → use get_current_time:\n"
"• REQUIRED: timezone (string) - Use IANA timezone format\n"
"• EXAMPLES: 'America/Los_Angeles', 'Europe/London', 'UTC'\n"
"• USER CONTEXT: Infer timezone from user location or explicitly ask\n"
"• ERROR HANDLING: Default to UTC if timezone invalid\n"
"\n"
"USAGE REASONING: This tool provides precise time information for scheduling,\n"
"coordination, and time-aware responses. Always explain timezone context."
```

**Specific Agent Backstory Addition:**
```python
"For TIME-RELATED queries, I use get_current_time with precise timezone handling.\n"
"I analyze user context (location, schedule, preferences) to select appropriate\n"
"timezones and provide time information that supports scheduling decisions."
```

#### **calculate_time_difference**

**Agent Prompt Integration:**
```python
"For TIME CALCULATIONS → use calculate_time_difference:\n"
"• REQUIRED: start_date (string), end_date (string)\n"
"• FORMAT: ISO date format or natural language dates\n"
"• USE CASES: Meeting duration, deadline countdown, age calculation\n"
"• CONTEXT AWARENESS: Consider user's timezone for date interpretation"
```

#### **format_date**

**Agent Prompt Integration:**
```python
"For DATE FORMATTING → use format_date:\n"
"• REQUIRED: date_string (string), format_string (string)\n"
"• INTELLIGENCE: Choose format based on user locale and context\n"
"• EXAMPLES: 'MM/dd/yyyy' (US), 'dd/MM/yyyy' (EU), 'yyyy-MM-dd' (ISO)"
```

### 🌤️ Weather Tools

#### **local_weather**

**Agent Prompt Integration:**
```python
"For LOCAL WEATHER → use local_weather:\n"
"• REQUIRED: location (string)\n"
"• OPTIONAL: data_dir (string) for cached data\n"
"• LOCATION INTELLIGENCE: Accept city names, coordinates, or addresses\n"
"• CONTEXT ENRICHMENT: Provide relevant weather context for user activities"
```

**Weather Agent Backstory Pattern:**
```python
"🌤️ WEATHER EXPERTISE:\n"
"I provide comprehensive weather information using local_weather and weather_api tools.\n"
"My weather analysis includes:\n"
"• Current conditions with activity recommendations\n"
"• Location-aware forecasting with travel implications\n"
"• Context-appropriate weather formatting (detailed vs brief)\n"
"• Integration with calendar events for weather-dependent planning"
```

#### **weather_api**

**Agent Prompt Integration:**
```python
"For COMPREHENSIVE WEATHER → use weather_api:\n"
"• REQUIRED: location (string)\n"
"• OPTIONAL: units ('metric'|'imperial'|'standard'), forecast (boolean), days (1-5)\n"
"• INTELLIGENCE: Choose units based on user location/preference\n"
"• FORECASTING: Include forecast for planning-related queries"
```

#### **format_weather**

**Agent Prompt Integration:**
```python
"For WEATHER PRESENTATION → use format_weather:\n"
"• REQUIRED: weather_data (object)\n"
"• OPTIONAL: format ('simple'|'detailed'|'forecast')\n"
"• CONTEXT ADAPTATION: Choose format based on user query complexity\n"
"• USER EXPERIENCE: Prioritize readability and actionable information"
```

### 🧠 Memory & Conversation Tools

#### **extract_conversation_entities**

**Agent Prompt Integration:**
```python
"For CONVERSATION ANALYSIS → use extract_conversation_entities:\n"
"• REQUIRED: conversation_text (string)\n"
"• OPTIONAL: conversation_id (string), min_confidence (0.0-1.0)\n"
"• INTELLIGENCE: Extract people, places, events, topics automatically\n"
"• MEMORY INTEGRATION: Store extracted entities for future reference\n"
"• CONFIDENCE TUNING: Adjust threshold based on text quality/length"
```

**Memory Agent Backstory Pattern:**
```python
"🧠 CONVERSATION INTELLIGENCE:\n"
"I analyze conversations using extract_conversation_entities to identify:\n"
"• People mentioned (names, relationships, context)\n"
"• Places discussed (locations, venues, addresses)\n"
"• Events referenced (meetings, activities, deadlines)\n"
"• Topics and themes (projects, interests, concerns)\n"
"• Emotional context and sentiment patterns\n"
"\n"
"My entity extraction considers context, co-references, and implicit mentions\n"
"to build comprehensive understanding of conversation content."
```

#### **extract_from_conversation_history**

**Agent Prompt Integration:**
```python
"For HISTORICAL ANALYSIS → use extract_from_conversation_history:\n"
"• REQUIRED: conversation_history (string)\n"
"• OPTIONAL: extraction_types (array), max_entity_confidence (float)\n"
"• SCOPE: Process multiple conversations for pattern analysis\n"
"• INTELLIGENCE: Identify trends, recurring topics, relationship evolution"
```

#### **infer_conversation_intent**

**Agent Prompt Integration:**
```python
"For INTENT ANALYSIS → use infer_conversation_intent:\n"
"• REQUIRED: conversation_text (string)\n"
"• OPTIONAL: intent_types (array), auto_update (boolean)\n"
"• INTELLIGENCE: Detect actionable intents (create, update, schedule, search)\n"
"• AUTOMATION: Optionally trigger automatic actions based on detected intent"
```

### 📅 Calendar Management Tools

#### **calendar_query**

**Agent Prompt Integration:**
```python
"For CALENDAR OPERATIONS → use calendar_query:\n"
"• REQUIRED: action ('query'|'get_todays_events'|'get_events_for_date'|\n"
"           'get_upcoming_events'|'set_user')\n"
"• CONTEXT-DEPENDENT: query (string), date (YYYY-MM-DD), days (number), user_id\n"
"• INTELLIGENCE: Choose action based on user query specificity\n"
"• EXAMPLES:\n"
"  - 'What meetings do I have today?' → action: 'get_todays_events'\n"
"  - 'Show me next week's schedule' → action: 'get_upcoming_events', days: 7\n"
"  - 'Any meetings on Friday?' → action: 'get_events_for_date', date: '2025-06-13'"
```

**Calendar Agent Reasoning Pattern:**
```python
"CALENDAR QUERY DECISION FRAMEWORK:\n"
"1. Analyze temporal references in user query\n"
"2. Determine if query is about today, specific date, or range\n"
"3. Select appropriate action parameter\n"
"4. Include relevant context (user_id, date range)\n"
"5. Format response with scheduling insights and conflicts"
```

### 💰 Finance Tools

#### **finance_tool**

**Agent Prompt Integration:**
```python
"For FINANCIAL OPERATIONS → use finance_tool:\n"
"• REQUIRED: action ('create'|'update'|'delete'|'categorize'|'add_tag'|'add_item')\n"
"• CONTEXT-DEPENDENT:\n"
"  - transaction_data (object) for create/update\n"
"  - transaction_id (string) for update/delete/categorize/add_tag\n"
"  - category (string) for categorize\n"
"  - tag (string) for add_tag\n"
"  - item (object) for add_item\n"
"• INTELLIGENCE: Infer action from user intent and data availability"
```

#### **get_recent_expenses**

**Agent Prompt Integration:**
```python
"For EXPENSE RETRIEVAL → use get_recent_expenses:\n"
"• REQUIRED: days (number), category (string), min_amount (string), limit (number)\n"
"• INTELLIGENCE: Set reasonable defaults based on query context\n"
"• FILTERING: Use category='all' for broad searches\n"
"• AMOUNT HANDLING: Convert user amounts to string format"
```

#### **search_transactions**

**Agent Prompt Integration:**
```python
"For TRANSACTION SEARCH → use search_transactions:\n"
"• REQUIRED: All parameters are technically required but can use defaults\n"
"• INTELLIGENCE: Convert natural language to structured search\n"
"• EXAMPLES:\n"
"  - 'Coffee purchases last month' → query: 'coffee', category: 'food',\n"
"    start_date: '2025-05-01', end_date: '2025-05-31'\n"
"  - 'Expensive purchases over $100' → min_amount: '100.00'"
```

### 🏥 Health Tools

#### **health_query**

**Agent Prompt Integration:**
```python
"For HEALTH DATA → use health_query:\n"
"• REQUIRED: action ('query'|'get_summary'|'get_activity'|'get_sleep'|'set_user')\n"
"• INTELLIGENT ROUTING:\n"
"  - General questions → action: 'query', query: natural language\n"
"  - Health overview → action: 'get_summary'\n"
"  - Exercise data → action: 'get_activity'\n"
"  - Sleep analysis → action: 'get_sleep'\n"
"• PRIVACY: Always respect health data sensitivity"
```

**Health Agent Specialized Reasoning:**
```python
"🏥 HEALTH DATA ANALYSIS EXPERTISE:\n"
"I analyze health queries to determine the most appropriate action:\n"
"• 'How did I sleep?' → get_sleep action for detailed sleep analysis\n"
"• 'Show my activity today' → get_activity for exercise/movement data\n"
"• 'Health summary' → get_summary for comprehensive overview\n"
"• 'How many steps yesterday?' → query action with specific question\n"
"\n"
"Privacy-First Approach: I handle health data with maximum discretion,\n"
"provide contextual insights without exposing raw data unnecessarily."
```

### 📄 Document Processing Tools

#### **process_document**

**Agent Prompt Integration:**
```python
"For DOCUMENT PROCESSING → use process_document:\n"
"• REQUIRED: file_path (string)\n"
"• OPTIONAL: use_ocr, extract_tables, extract_forms, extract_images,\n"
"           return_metadata_only (all boolean)\n"
"• INTELLIGENCE: Choose processing options based on document type and user intent\n"
"• FILE SUPPORT: PDF, DOC, DOCX, TXT, images with OCR"
```

#### **summarize_document**

**Agent Prompt Integration:**
```python
"For DOCUMENT SUMMARIZATION → use summarize_document:\n"
"• REQUIRED: file_path (string)\n"
"• OPTIONAL: max_length (number), include_key_points (boolean)\n"
"• INTELLIGENCE: Adjust summary length based on document size and user needs\n"
"• CONTEXT AWARENESS: Include key points for research-oriented queries"
```

#### **search_document**

**Agent Prompt Integration:**
```python
"For DOCUMENT SEARCH → use search_document:\n"
"• REQUIRED: file_path (string), query (string)\n"
"• OPTIONAL: limit (number), include_context (boolean)\n"
"• INTELLIGENCE: Extract user search intent and provide relevant context\n"
"• RELEVANCE: Include surrounding context for better understanding"
```

### 📈 Text Analysis Tools

#### **analyze_sentiment**

**Agent Prompt Integration:**
```python
"For SENTIMENT ANALYSIS → use analyze_sentiment:\n"
"• REQUIRED: text (string)\n"
"• OPTIONAL: provider (string)\n"
"• INTELLIGENCE: Provide nuanced sentiment interpretation\n"
"• CONTEXT: Connect sentiment to conversation patterns and user state"
```

#### **analyze_text**

**Agent Prompt Integration:**
```python
"For COMPREHENSIVE TEXT ANALYSIS → use analyze_text:\n"
"• REQUIRED: text (string)\n"
"• OPTIONAL: analysis_types (array), provider (string)\n"
"• INTELLIGENCE: Select analysis types based on text content and purpose\n"
"• MULTI-MODAL: Combine sentiment, entities, keywords, and summary"
```

## 🎯 Agent-Specific Tool Integration Patterns

### Personal Assistant Agent Tool Usage

```python
"🔧 PERSONAL ASSISTANT TOOL MASTERY:\n"
"• TEMPORAL INTELLIGENCE → get_current_time, calculate_time_difference\n"
"• CALENDAR MANAGEMENT → calendar_query with intelligent action selection\n"
"• WEATHER AWARENESS → local_weather, weather_api with location context\n"
"• CONVERSATION PROCESSING → extract_conversation_entities for insights\n"
"\n"
"TOOL SELECTION INTELLIGENCE:\n"
"I analyze each request to determine:\n"
"1. Primary intent (time, schedule, weather, information)\n"
"2. Required tool capabilities and parameters\n"
"3. Context enrichment opportunities\n"
"4. User preference patterns for output format\n"
"5. Opportunity for proactive assistance"
```

### Memory Librarian Agent Tool Usage

```python
"🧠 MEMORY LIBRARIAN TOOL EXPERTISE:\n"
"• ENTITY EXTRACTION → extract_conversation_entities with confidence tuning\n"
"• INTENT DETECTION → infer_conversation_intent with auto-update capability\n"
"• HISTORICAL ANALYSIS → extract_from_conversation_history for patterns\n"
"• RELATIONSHIP MAPPING → Connect entities across conversations and time\n"
"\n"
"MEMORY INTEGRATION INTELLIGENCE:\n"
"I use sophisticated analysis to:\n"
"1. Extract entities with context-aware confidence thresholds\n"
"2. Infer user intents for proactive memory updates\n"
"3. Cross-reference new information with existing memory\n"
"4. Maintain relationship consistency and temporal accuracy\n"
"5. Provide contextual memory retrieval with relevance ranking"
```

### Research Specialist Agent Tool Usage

```python
"🔍 RESEARCH SPECIALIST TOOL MASTERY:\n"
"• DOCUMENT PROCESSING → process_document with intelligent option selection\n"
"• CONTENT ANALYSIS → analyze_text, summarize_document, search_document\n"
"• SENTIMENT TRACKING → analyze_sentiment for content evaluation\n"
"• ENTITY RECOGNITION → extract_entities for research organization\n"
"\n"
"RESEARCH METHODOLOGY INTELLIGENCE:\n"
"I apply systematic analysis to:\n"
"1. Choose appropriate document processing based on file type and purpose\n"
"2. Adapt summarization length and detail to research depth required\n"
"3. Extract relevant entities and themes for knowledge organization\n"
"4. Provide source attribution and confidence levels for findings\n"
"5. Connect research findings to existing knowledge base"
```

### Finance Tracker Agent Tool Usage

```python
"💰 FINANCE TRACKER TOOL EXPERTISE:\n"
"• TRANSACTION MANAGEMENT → finance_tool with action-based intelligence\n"
"• EXPENSE ANALYSIS → get_recent_expenses, get_spending_summary\n"
"• SEARCH CAPABILITIES → search_transactions with natural language processing\n"
"• FINANCIAL INSIGHTS → Cross-tool analysis for spending patterns\n"
"\n"
"FINANCIAL INTELLIGENCE:\n"
"I provide sophisticated financial analysis by:\n"
"1. Converting natural language queries to structured financial searches\n"
"2. Selecting appropriate time ranges and categories based on context\n"
"3. Providing spending insights with trend analysis and recommendations\n"
"4. Maintaining transaction categorization accuracy and consistency\n"
"5. Offering proactive budget alerts and optimization suggestions"
```

### Health Analyst Agent Tool Usage

```python
"🏥 HEALTH ANALYST TOOL MASTERY:\n"
"• HEALTH QUERIES → health_query with intelligent action routing\n"
"• DATA ANALYSIS → health_query_simple, health_summary_simple for streamlined access\n"
"• PATTERN RECOGNITION → Cross-temporal health trend analysis\n"
"• PRIVACY PROTECTION → Secure health data handling with user consent\n"
"\n"
"HEALTH INTELLIGENCE:\n"
"I provide comprehensive health analysis through:\n"
"1. Intelligent routing of health queries to appropriate data sources\n"
"2. Privacy-first health data presentation with contextual insights\n"
"3. Trend analysis connecting current metrics to historical patterns\n"
"4. Actionable health recommendations based on data patterns\n"
"5. Integration of health data with calendar and activity planning"
```

## 🔄 Tool Execution Error Handling

### Universal Error Handling Pattern

```python
"TOOL EXECUTION ERROR RECOVERY:\n"
"1. VALIDATION ERRORS → Provide parameter guidance and examples\n"
"2. TIMEOUT ERRORS → Suggest simplified queries or alternative approaches\n"
"3. SERVICE UNAVAILABLE → Gracefully explain limitations and offer alternatives\n"
"4. AUTHENTICATION ERRORS → Guide user through credential setup\n"
"5. DATA ERRORS → Validate inputs and suggest corrections\n"
"\n"
"ERROR COMMUNICATION PATTERN:\n"
"• Acknowledge the issue transparently\n"
"• Explain what went wrong in user-friendly terms\n"
"• Provide specific guidance for resolution\n"
"• Offer alternative approaches when possible\n"
"• Learn from errors to improve future interactions"
```

## 🧪 Tool Testing and Validation

### Agent Tool Testing Prompts

```python
"TOOL VALIDATION PROCESS:\n"
"Before executing any tool, I validate:\n"
"1. Parameter completeness and format correctness\n"
"2. User context and permission requirements\n"
"3. Expected outcome alignment with user query\n"
"4. Error handling and fallback strategies\n"
"5. Response format and user experience optimization\n"
"\n"
"POST-EXECUTION VALIDATION:\n"
"After tool execution, I verify:\n"
"1. Response relevance and accuracy\n"
"2. User satisfaction with information provided\n"
"3. Opportunities for follow-up actions\n"
"4. Learning opportunities for future improvements\n"
"5. Integration success with overall conversation flow"
```

## 📊 Performance Optimization

### Tool Usage Analytics Pattern

```python
"TOOL PERFORMANCE INTELLIGENCE:\n"
"I continuously optimize tool usage by:\n"
"• Tracking tool execution success rates and user satisfaction\n"
"• Learning optimal parameter combinations for different contexts\n"
"• Identifying tool combination patterns that enhance user experience\n"
"• Adapting tool selection based on user behavior and preferences\n"
"• Proactively suggesting tool combinations for complex tasks"
```

This guide provides the foundational patterns for integrating CrewAI agents with the Myndy-AI tool ecosystem. Each tool category requires specific understanding of parameters, context, and intelligent usage patterns to deliver optimal user experience.

---

**Key Implementation Notes:**

1. **HTTP-First Architecture**: All tools execute via FastAPI HTTP endpoints
2. **Parameter Intelligence**: Agents must understand required vs optional parameters
3. **Context Awareness**: Tool selection considers user context, preferences, and history
4. **Error Resilience**: Graceful handling of tool failures with alternative approaches
5. **Continuous Learning**: Agents improve tool usage based on success patterns and user feedback

**Last Updated**: 2025-06-10  
**Tool Integration**: FastAPI service-oriented architecture with 530+ specialized tools