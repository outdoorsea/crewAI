# CrewAI Agent Prompt Engineering Guide

## Overview

This guide provides comprehensive prompt engineering best practices for CrewAI agents to effectively use tools and deliver optimal performance. Based on analysis of successful agent implementations, this document outlines proven patterns for role definition, goal structure, backstory creation, and tool integration.

## 🎯 Core Prompt Engineering Principles

### 1. **Agent-Based Tool Selection (MANDATORY)**

**CRITICAL REQUIREMENT**: ALL tool selection MUST be performed by intelligent agents using LLM reasoning, NOT by keyword patterns or rule-based systems.

```python
# ✅ CORRECT: Agent-based tool selection
"Analyze the user request and select appropriate tools based on these criteria:
1. Request intent and complexity analysis
2. Domain expertise requirements assessment  
3. Tool capability mapping to user needs
4. Reasoning transparency for tool choices
5. Expected outcome and quality optimization"

# ❌ INCORRECT: Rule-based tool selection
"If request contains 'weather', use weather tools"
"If request mentions 'time', use time tools"
```

### 2. **LLM-Driven Decision Making**

Agents should use sophisticated reasoning rather than simple pattern matching:

```python
backstory="Unlike simple rule-based systems, I use advanced reasoning to understand "
          "context, nuance, tone, and implicit meanings. My analysis goes beyond "
          "keyword matching to provide intelligent, contextually-aware responses."
```

### 3. **Reasoning Transparency**

Always require agents to explain their decision-making process:

```python
"For every tool selection, provide reasoning including:
• Why this tool was chosen over alternatives
• How it addresses the specific user need
• What factors influenced the decision
• What outcome is expected from tool usage"
```

## 🏗️ Agent Structure Framework

### Role Definition Pattern

**Format**: Clear, descriptive, domain-specific roles

```python
# Standard Agent
role="Personal Assistant"

# Enhanced Agent  
role="Enhanced Personal Assistant with Memory Intelligence"

# Specialized Agent
role="Enhanced Behavioral Intelligence Observer with Memory Integration"
```

**Best Practices**:
- Use specific, descriptive role names
- Include specialization when relevant
- Avoid generic terms like "AI Assistant"
- Make the expertise domain immediately clear

### Goal Structure Pattern

**Framework**: Action-oriented goals with explicit tool usage guidance

```python
goal=(
    "Primary objective: [Core responsibility and outcomes]"
    "\n\n"
    "ENHANCED with [additional capabilities]: [specific enhancements]"
    "\n\n" 
    "🎯 TOOL USAGE GUIDANCE:\n"
    "• [Domain 1]: [specific tools] for [specific use cases]\n"
    "• [Domain 2]: [specific tools] for [specific use cases]\n"
    "• [Domain 3]: [specific tools] for [specific use cases]\n"
    "\n"
    "CRITICAL: [Boundaries and anti-patterns]"
)
```

**Example**:
```python
goal=(
    "Efficiently manage calendar events, process emails, organize contacts, "
    "and deliver proactive assistance for daily productivity."
    "\n\n"
    "ENHANCED with memory capabilities: search personal memory, manage relationships, "
    "extract insights from conversations, maintain contextual awareness."
    "\n\n"
    "🎯 TOOL USAGE GUIDANCE:\n"
    "• 📅 SCHEDULING: calendar_query, get_current_time for time-related tasks\n"
    "• 🌤️ WEATHER: local_weather, format_weather for weather queries\n"
    "• 🧠 MEMORY: search_memory, create_person for knowledge management\n"
    "• 💬 CONVERSATIONS: extract_conversation_entities for analysis\n"
    "\n"
    "CRITICAL: Use specific tools for specific purposes. Never use "
    "conversation tools for weather queries or weather tools for memory tasks."
)
```

### Backstory Structure Pattern

**Framework**: Professional experience + methodology + tool integration + expertise

```python
backstory=(
    "[Professional background with credible experience]"
    "\n\n"
    "🎯 CORE EXPERTISE:\n"
    "• [Expertise area 1 with specific capabilities]\n"
    "• [Expertise area 2 with specific capabilities]\n" 
    "• [Expertise area 3 with specific capabilities]\n"
    "\n\n"
    "🧠 [ENHANCED CAPABILITIES SECTION]:\n"
    "• [Enhanced capability 1 with methodology]\n"
    "• [Enhanced capability 2 with methodology]\n"
    "• [Enhanced capability 3 with methodology]\n"
    "\n\n"
    "🔧 TOOL USAGE EXPERTISE:\n"
    "For [TASK TYPE] → use [specific tools]\n"
    "For [TASK TYPE] → use [specific tools]\n"
    "For [TASK TYPE] → use [specific tools]\n"
    "\n\n"
    "⚠️ CRITICAL BOUNDARIES:\n"
    "[Clear anti-patterns and boundaries]\n"
    "\n\n"
    "[Concluding statement about unique value proposition]"
)
```

## 🔧 Tool Integration Patterns

### Explicit Tool Mapping

Always provide clear, specific tool-to-task mappings:

```python
"For WEATHER queries → use local_weather, format_weather, weather_api\n"
"For TIME queries → use get_current_time\n"
"For MEMORY search → use search_memory with appropriate model types\n"
"For PEOPLE management → use create_person, search people entities\n"
"For CONVERSATION analysis → use extract_conversation_entities, infer_conversation_intent"
```

### Anti-Pattern Specification

Explicitly state what NOT to do:

```python
"⚠️ CRITICAL BOUNDARIES:\n"
"NEVER use conversation analysis tools for weather or time queries.\n"
"NEVER use weather tools for memory or conversation tasks.\n"
"ALWAYS select the most appropriate tool for the specific task type."
```

### Tool Selection Decision Framework

Provide structured decision-making criteria:

```python
"Tool Selection Process:
1. Analyze request intent and domain requirements
2. Map required capabilities to available tools  
3. Consider user context and historical preferences
4. Select optimal tool combination for task complexity
5. Validate tool selection against request objectives
6. Execute with reasoning transparency"
```

## 🧠 Memory Integration Patterns

### Memory-Enhanced Agents

For agents with memory capabilities, structure prompts to integrate historical context:

```python
"🧠 MEMORY INTELLIGENCE CAPABILITIES:\n"
"• Deep knowledge of personal relationships and professional networks\n"
"• Context extraction from conversations and communications\n" 
"• Pattern recognition in behavior, preferences, and decision-making\n"
"• Proactive insight generation from historical interactions\n"
"• Comprehensive personal and professional profile management"
```

### Memory Tool Usage Guidance

Provide specific instructions for memory tool usage:

```python
"🔧 MEMORY TOOL INTEGRATION:\n"
"• search_memory → [specific use case and expected outcomes]\n"
"• extract_conversation_entities → [specific use case and expected outcomes]\n"
"• store_conversation_analysis → [specific use case and expected outcomes]\n"
"• get_conversation_summary → [specific use case and expected outcomes]\n"
"• infer_conversation_intent → [specific use case and expected outcomes]"
```

### Cross-Temporal Analysis

For memory-enhanced agents, include temporal analysis requirements:

```python
"Cross-Temporal Intelligence:
• Compare current patterns with historical baselines
• Identify evolution trends and preference changes
• Validate new observations against established patterns
• Generate predictive insights based on behavioral trajectories
• Update models with new learning while preserving validated patterns"
```

## 👥 Collaborative Agent Patterns

### Delegation Criteria

Provide clear criteria for when to collaborate vs. work independently:

```python
"Collaboration Decision Framework:
• Simple tasks (< 3 tools, single domain): Handle directly
• Complex tasks (> 3 tools, cross-domain): Consider collaboration
• Specialized expertise outside domain: Delegate to appropriate agent
• User preference for specific agent: Honor user choice
• Quality optimization opportunity: Suggest collaborative approach"
```

### Context Sharing

Define how agents should share context during collaboration:

```python
"Context Sharing Protocol:
1. Provide relevant background and task context
2. Share user preferences and interaction patterns
3. Include relationship and historical context
4. Specify expected collaboration outcome
5. Maintain context coherence across agent interactions"
```

## 🎭 Specialized Agent Patterns

### Shadow Agent Pattern

For behavioral observation agents:

```python
"Silent Operation Protocol:
• NEVER respond directly to users - work collaboratively only
• Focus on behavioral pattern recognition and context synthesis
• Provide insights to enhance other agents' responses
• Continuously learn and update behavioral models
• Maintain user privacy while optimizing experience"
```

### Memory Librarian Pattern

For memory management agents:

```python
"Memory Management Protocol:
• Maintain comprehensive knowledge organization
• Ensure data consistency and relationship integrity
• Provide contextual memory retrieval with relevance ranking
• Update memory models based on new interactions
• Balance detail preservation with privacy considerations"
```

### Personal Assistant Pattern

For productivity and organization agents:

```python
"Productivity Optimization Protocol:
• Anticipate needs based on patterns and context
• Provide proactive recommendations and reminders
• Optimize workflows and reduce friction points
• Maintain awareness of priorities and preferences
• Balance efficiency with thoroughness"
```

## 📊 Quality Assurance Patterns

### Response Validation

Include quality checking requirements:

```python
"Response Quality Framework:
• Verify tool outputs are relevant and accurate
• Ensure response completeness matches user needs
• Validate reasoning transparency and logic
• Check for appropriate personalization and context
• Confirm alignment with user preferences and patterns"
```

### Error Handling

Define graceful error handling approaches:

```python
"Error Recovery Protocol:
• Acknowledge tool failures transparently
• Provide alternative approaches when primary tools fail
• Explain limitations and suggest workarounds
• Maintain user experience quality during degraded functionality
• Learn from failures to improve future interactions"
```

### Continuous Improvement

Include learning and adaptation mechanisms:

```python
"Continuous Learning Framework:
• Analyze interaction success and failure patterns
• Update tool selection strategies based on outcomes
• Refine personalization approaches based on feedback
• Improve reasoning accuracy through pattern recognition
• Enhance collaboration effectiveness through experience"
```

## 🔄 Implementation Workflow

### 1. Agent Definition Phase
1. Define clear role and domain expertise
2. Specify enhanced capabilities and unique value
3. Map available tools to agent responsibilities
4. Define collaboration patterns and delegation criteria

### 2. Prompt Engineering Phase
1. Structure goal with tool usage guidance
2. Create comprehensive backstory with methodology
3. Include explicit tool mapping and anti-patterns
4. Add quality assurance and error handling requirements

### 3. Tool Integration Phase
1. Implement agent-based tool selection logic
2. Add reasoning transparency requirements
3. Include context sharing and collaboration protocols
4. Define memory integration patterns (if applicable)

### 4. Testing and Validation Phase
1. Test tool selection accuracy and reasoning
2. Validate collaboration effectiveness
3. Verify error handling and recovery mechanisms
4. Assess continuous learning and improvement

## 📝 Prompt Templates

### Basic Agent Template
```python
role="[Specific Role with Domain Expertise]"

goal=(
    "[Primary objective and responsibilities]"
    "\n\n"
    "🎯 TOOL USAGE GUIDANCE:\n"
    "• [Domain]: [tools] for [use cases]\n"
    "\n"
    "CRITICAL: [Boundaries and anti-patterns]"
)

backstory=(
    "[Professional background and credibility]"
    "\n\n"
    "🔧 TOOL EXPERTISE:\n"
    "[Specific tool usage patterns and methodologies]"
    "\n\n"
    "⚠️ BOUNDARIES:\n"
    "[Clear limitations and anti-patterns]"
)
```

### Enhanced Agent Template
```python
role="Enhanced [Role] with [Enhanced Capabilities]"

goal=(
    "[Core responsibilities] ENHANCED with [specific enhancements]: "
    "[detailed enhancement descriptions]"
    "\n\n"
    "🎯 TOOL USAGE GUIDANCE:\n"
    "• [Domain 1]: [tools] for [use cases]\n"
    "• [Domain 2]: [tools] for [use cases]\n"
    "• [Enhanced Domain]: [enhanced tools] for [enhanced capabilities]\n"
    "\n"
    "CRITICAL: [Enhanced boundaries and reasoning requirements]"
)

backstory=(
    "[Enhanced professional background]"
    "\n\n"
    "🎯 CORE EXPERTISE:\n"
    "[Traditional capabilities with enhanced context]"
    "\n\n"
    "🧠 ENHANCED CAPABILITIES:\n"
    "[Detailed enhanced capability descriptions]"
    "\n\n"
    "🔧 ENHANCED TOOL INTEGRATION:\n"
    "[Sophisticated tool usage patterns and methodologies]"
    "\n\n"
    "⚠️ CRITICAL BOUNDARIES:\n"
    "[Comprehensive limitations and anti-patterns]"
)
```

## 🚀 Advanced Patterns

### Multi-Modal Intelligence Integration
For agents that combine multiple types of intelligence:

```python
"Multi-Modal Analysis Framework:
• Behavioral pattern recognition with memory correlation
• Relationship dynamics analysis with network effects
• Temporal pattern analysis with predictive modeling
• Cross-domain context synthesis with validation
• Preference evolution tracking with adaptation mechanisms"
```

### Predictive Context Generation
For agents that provide proactive assistance:

```python
"Predictive Intelligence Framework:
• Analyze current context against historical patterns
• Identify likely future needs and information requirements
• Generate proactive recommendations with confidence levels
• Anticipate collaboration opportunities and optimization potential
• Provide predictive context for enhanced user experience"
```

This guide provides the foundation for creating effective, intelligent CrewAI agents that use tools appropriately, collaborate effectively, and continuously improve their performance through sophisticated reasoning and learning mechanisms.