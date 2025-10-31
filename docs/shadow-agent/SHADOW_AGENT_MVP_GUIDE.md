# Shadow Agent MVP - Behavioral Intelligence Observer

## Overview

The Shadow Agent MVP is a behavioral intelligence system that works silently in the background to observe user interactions, analyze patterns, and store insights for improved personalization. It integrates seamlessly with the OpenWebUI pipeline and CrewAI agent system.

## Features

### 🔮 Core Capabilities

- **Silent Observation**: Runs in background without interfering with user interactions
- **Behavioral Pattern Recognition**: Analyzes communication styles, message types, and preferences
- **Memory Integration**: Stores observations via myndy-ai memory APIs (journal entries, status updates, facts)
- **Personality Insights**: Generates behavioral summaries and insights over time
- **OpenWebUI Integration**: Automatically observes all pipeline conversations

### 🧠 Behavioral Analysis

The Shadow Agent analyzes:

- **Communication Style**: concise, detailed, polite, urgent, casual
- **Message Types**: question, request, appreciation, scheduling, memory_storage, general
- **Topic Interests**: health, finance, work, calendar, personal, technology, weather
- **Emotional Indicators**: happy, frustrated, confused, excited, worried, neutral
- **Usage Patterns**: time of day, urgency levels, complexity preferences

## Architecture

### Components

1. **MVP Shadow Agent** (`agents/mvp_shadow_agent.py`)
   - Standalone behavioral observation class
   - HTTP client for myndy-ai API integration
   - Pattern analysis and insight generation

2. **CrewAI Shadow Agent** (`agents/shadow_agent.py`)
   - CrewAI agent wrapper for crew integration
   - Collaborative behavioral analysis
   - Tool-based observation capabilities

3. **Pipeline Integration** (`pipeline/crewai_myndy_pipeline.py`)
   - Background observation threads
   - Automatic conversation analysis
   - Session-based tracking

### Data Flow

```
User Message → Primary Agent → Response
     ↓
Shadow Agent (Background) → Behavioral Analysis → Memory Storage
     ↓
Pattern Recognition → Insights → Personality Modeling
```

## API Integration

### Myndy-AI Memory APIs Used

- **Journal Entries** (`/api/v1/memory/journal`): Store detailed behavioral observations
- **Status Updates** (`/api/v1/status/update`): Track current behavioral patterns
- **Facts Storage** (`/api/v1/memory/facts`): Store long-term behavioral preferences
- **Memory Search** (`/api/v1/memory/search`): Retrieve behavioral history for analysis

### Authentication

The Shadow Agent requires API authentication to store data in myndy-ai:

```python
headers = {
    "Content-Type": "application/json", 
    "User-Agent": "MVP-Shadow-Agent/1.0",
    "X-API-Key": "your-api-key"  # Required for myndy-ai API access
}
```

## Usage

### Standalone Usage

```python
from agents.mvp_shadow_agent import create_mvp_shadow_agent

# Create Shadow Agent
shadow_agent = create_mvp_shadow_agent()

# Observe a conversation
observation = shadow_agent.observe_conversation(
    user_message="What's the weather like today?",
    agent_response="It's sunny and 72°F in your area.",
    agent_type="personal_assistant",
    session_id="session_123"
)

# Get behavioral insights
insights = shadow_agent.get_behavioral_insights()

# Generate personality summary
summary = shadow_agent.generate_personality_summary()
```

### OpenWebUI Pipeline Integration

The Shadow Agent is automatically enabled in the OpenWebUI pipeline:

1. **Automatic Observation**: Every conversation is observed in background threads
2. **Session Tracking**: Conversations are tracked by session for pattern analysis
3. **Zero User Impact**: Observations run asynchronously without affecting response times

```python
# In pipeline/crewai_myndy_pipeline.py
def _execute_shadow_observation(self, user_message: str, agent_response: str, 
                               agent_type: str, session_id: str) -> None:
    """Execute MVP Shadow Agent observation in background"""
    if not self.mvp_shadow_agent:
        return
        
    # Run observation in background thread
    observer_thread = threading.Thread(
        target=lambda: self.mvp_shadow_agent.observe_conversation(
            user_message, agent_response, agent_type, session_id
        ), 
        daemon=True
    )
    observer_thread.start()
```

## Configuration

### Environment Setup

1. **Myndy-AI Server**: Ensure myndy-ai FastAPI server is running on `http://localhost:8000`
2. **API Authentication**: Configure API key for myndy-ai access
3. **CrewAI Integration**: Shadow Agent is automatically available in agent routing

### Pipeline Valves

```python
class Valves(BaseModel):
    enable_shadow_observation: bool = True  # Enable/disable Shadow Agent
    shadow_api_base_url: str = "http://localhost:8000"  # Myndy-AI server URL
    shadow_debug_mode: bool = False  # Enable detailed logging
```

## Testing

### Test Suite

Run the integration test suite:

```bash
cd /Users/jeremy/myndy-core/crewAI
python test_shadow_agent_integration.py
```

### Test Categories

1. **MVP Shadow Agent Standalone**: Tests basic observation functionality
2. **Shadow Agent Creation**: Tests CrewAI agent creation and configuration
3. **Shadow Agent Tools**: Tests tool integration and availability
4. **Pipeline Integration**: Tests OpenWebUI pipeline integration
5. **Crew Integration**: Tests Shadow Agent in crew system
6. **Routing System**: Tests intelligent routing configuration

## Data Storage

### Behavioral Observations (Journal Entries)

```json
{
  "content": "Shadow Agent Observation: question message with polite style",
  "category": "behavioral_observation",
  "mood": "neutral",
  "tags": ["weather", "question", "polite"],
  "metadata": {
    "session_id": "session_123",
    "message_length": 28,
    "urgency_level": "low",
    "time_of_day": 14,
    "complexity": "simple",
    "emotional_indicators": ["neutral"],
    "observation_source": "shadow_agent"
  }
}
```

### Behavioral Patterns (Status Updates)

```json
{
  "mood": "neutral",
  "activity": "interacting_with_personal_assistant",
  "notes": "Communication style: polite, Message type: question, Topics: weather",
  "availability": "available"
}
```

### Behavioral Facts (Long-term Learning)

```json
{
  "content": "User prefers polite communication style and shows interest in weather, technology",
  "category": "behavioral_preference",
  "confidence": 0.7,
  "source": "shadow_agent",
  "tags": ["behavioral_pattern", "communication_preference", "weather", "technology"]
}
```

## Insights and Analytics

### Pattern Recognition

The Shadow Agent identifies patterns across multiple dimensions:

- **Communication Consistency**: Measures how consistent user communication style is
- **Topic Preferences**: Identifies frequently discussed topics
- **Time Patterns**: Tracks when user is most active
- **Agent Preferences**: Learns which agents user prefers for different tasks
- **Emotional Context**: Tracks emotional patterns and triggers

### Personality Modeling

Generated personality summaries include:

```
"Communication style: polite. Tends to use question messages. 
Interested in: weather, technology, health. Based on 15 behavioral observations."
```

## Routing Integration

### Intelligent Routing

The Shadow Agent is configured in the intelligent routing system but **never selected as primary agent**:

```python
"shadow_agent": {
    "keywords": ["pattern", "behavior", "preference", "learn", "observe"],
    "patterns": [
        r"learn.*about.*me|understand.*me|analyze.*behavior",
        r"what.*pattern|behavioral.*pattern"
    ],
    "description": "Silently observes user patterns, analyzes behavior, provides contextual insights (never primary responder)",
    "priority_multiplier": 0.0  # Never selected as primary agent
}
```

### Background Operation

- Shadow Agent runs **silently in background** for every conversation
- Provides **contextual insights** to primary agents
- **Never responds directly** to users
- **Continuous learning** from all interactions

## Security and Privacy

### Data Protection

- All behavioral data stored in encrypted myndy-ai memory system
- Session-based isolation prevents cross-contamination
- Configurable data retention policies
- User consent required for behavioral analysis

### Privacy Considerations

- Behavioral observations are **optional** and can be disabled
- Data remains **local** within myndy-ai system
- No external behavioral tracking or profiling
- User maintains **full control** over behavioral data

## Troubleshooting

### Common Issues

1. **API Authentication Errors (401)**
   - Ensure myndy-ai server is running
   - Configure proper API key in headers
   - Check server authentication settings

2. **Import Errors**
   - Verify project paths are correct
   - Ensure all dependencies are installed
   - Check CrewAI integration setup

3. **Tool Availability**
   - Some tools may require myndy-ai server
   - Check tool registry configuration
   - Verify memory system initialization

### Debug Mode

Enable debug logging for detailed observation tracking:

```python
shadow_agent = create_mvp_shadow_agent()
shadow_agent.logger.setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

- **Real-time Analytics Dashboard**: Live behavioral insights visualization
- **Predictive Modeling**: Anticipate user needs based on patterns
- **Multi-user Support**: Track behavioral patterns across multiple users
- **Advanced Emotional Intelligence**: Enhanced emotional state tracking
- **Cross-session Learning**: Long-term behavioral evolution tracking

### Integration Roadmap

- **External Analytics**: Integration with external behavioral analytics platforms
- **Machine Learning Models**: Advanced pattern recognition using ML
- **Personalization Engine**: Dynamic response personalization based on behavior
- **Feedback Loops**: User feedback integration for improved accuracy

## License

MIT License - See project LICENSE file for details.

---

**The Shadow Agent MVP provides the foundation for intelligent behavioral analysis and personalization in the Myndy AI ecosystem.**