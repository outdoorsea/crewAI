#!/usr/bin/env python3
"""
CrewAI Entity Management Agents

Specialized agents for detecting, extracting, and managing entities
in a Qdrant vector database using the entity extraction tools.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from crewai import Agent, Task, Crew, Process
from entity_extraction_tools import ENTITY_TOOLS

# === SPECIALIZED AGENTS ===

def create_entity_detector_agent():
    """Agent specialized in detecting and extracting entities from text."""
    return Agent(
        role="Entity Detection Specialist",
        goal="Accurately detect and extract people, places, organizations, projects, events, and other entities from text",
        backstory="""You are an expert in natural language processing and entity recognition. 
        You have years of experience identifying and categorizing different types of entities 
        from unstructured text. You understand context and can distinguish between different 
        entity types even when they might be ambiguous.""",
        llm="ollama/qwen2.5",  # Best reasoning for complex entity detection
        tools=[
            ENTITY_TOOLS[0],  # extract_entities_from_text
            ENTITY_TOOLS[1],  # extract_calendar_events  
            ENTITY_TOOLS[2],  # extract_contact_information
        ],
        verbose=True,
        allow_delegation=False
    )

def create_database_manager_agent():
    """Agent specialized in managing the Qdrant vector database."""
    return Agent(
        role="Knowledge Database Manager",
        goal="Efficiently store, search, update, and maintain entity information in the vector database",
        backstory="""You are a database specialist with expertise in vector databases and 
        knowledge management systems. You understand how to organize information for optimal 
        retrieval and maintain data quality. You're skilled at connecting related information 
        and finding patterns in stored data.""",
        llm="ollama/codellama",  # Best for database operations and API calls
        tools=[
            ENTITY_TOOLS[3],  # search_entities_in_qdrant
            ENTITY_TOOLS[4],  # store_entity_in_qdrant
            ENTITY_TOOLS[5],  # update_entity_in_qdrant
            ENTITY_TOOLS[6],  # get_entity_relationships
        ],
        verbose=True,
        allow_delegation=False
    )

def create_analytics_agent():
    """Agent specialized in analyzing entity data and trends."""
    return Agent(
        role="Entity Analytics Specialist", 
        goal="Analyze entity data to provide insights, trends, and recommendations",
        backstory="""You are a data analyst with expertise in knowledge graphs and 
        entity relationship analysis. You can identify patterns, trends, and insights 
        from entity data to help users understand their information landscape better.""",
        llm="ollama/qwen2.5",  # Best reasoning for analytics
        tools=[
            ENTITY_TOOLS[7],  # analyze_entity_trends
            ENTITY_TOOLS[3],  # search_entities_in_qdrant (for analysis)
            ENTITY_TOOLS[6],  # get_entity_relationships (for network analysis)
        ],
        verbose=True,
        allow_delegation=False
    )

def create_coordinator_agent():
    """Agent that coordinates between detection, storage, and analysis."""
    return Agent(
        role="Entity Management Coordinator",
        goal="Coordinate the complete entity management workflow from detection to storage to analysis",
        backstory="""You are a project manager specializing in information systems. 
        You understand the complete workflow of entity management and can coordinate 
        between different specialists to ensure comprehensive and accurate processing 
        of information.""",
        llm="ollama/llama3.2",  # Good balance for coordination tasks
        tools=ENTITY_TOOLS,  # Access to all tools for coordination
        verbose=True,
        allow_delegation=True
    )

# === EXAMPLE WORKFLOWS ===

def create_entity_extraction_workflow(input_text: str):
    """Create a complete entity extraction and storage workflow."""
    
    # Create agents
    detector = create_entity_detector_agent()
    db_manager = create_database_manager_agent()
    analytics = create_analytics_agent()
    
    # Create tasks
    detection_task = Task(
        description=f"""
        Analyze the following text and extract all entities:
        
        "{input_text}"
        
        Extract:
        1. People (names, roles, relationships)
        2. Organizations (companies, institutions)
        3. Locations (cities, countries, addresses)
        4. Projects (project names, descriptions)
        5. Events (meetings, deadlines, calendar items)
        6. Tasks (action items, todos)
        7. Contact information (emails, phones)
        
        Provide detailed extraction results with confidence scores and metadata.
        """,
        expected_output="Comprehensive JSON report of all extracted entities with metadata",
        agent=detector
    )
    
    storage_task = Task(
        description="""
        Take the extracted entities from the detection task and:
        
        1. Store each entity in the appropriate Qdrant collection
        2. Check for existing similar entities to avoid duplicates
        3. Update existing entities if new information is found
        4. Create relationships between related entities
        
        Provide a summary of what was stored and any updates made.
        """,
        expected_output="Summary report of storage operations and entity relationships",
        agent=db_manager
    )
    
    analysis_task = Task(
        description="""
        Analyze the newly stored entities and provide insights:
        
        1. Identify any interesting patterns or connections
        2. Check for trends in the data
        3. Suggest potential relationships that weren't automatically detected
        4. Provide recommendations for data organization
        
        Create a comprehensive analysis report.
        """,
        expected_output="Analysis report with insights and recommendations",
        agent=analytics
    )
    
    # Create crew with sequential process
    crew = Crew(
        agents=[detector, db_manager, analytics],
        tasks=[detection_task, storage_task, analysis_task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew

def create_entity_search_workflow(search_query: str, entity_type: str = "all"):
    """Create a workflow for searching and analyzing existing entities."""
    
    db_manager = create_database_manager_agent()
    analytics = create_analytics_agent()
    
    search_task = Task(
        description=f"""
        Search the vector database for entities related to: "{search_query}"
        
        Entity type focus: {entity_type}
        
        1. Perform a comprehensive search across relevant collections
        2. Find related entities and relationships
        3. Rank results by relevance and confidence
        """,
        expected_output="Detailed search results with relevance rankings",
        agent=db_manager
    )
    
    analysis_task = Task(
        description="""
        Analyze the search results and provide insights:
        
        1. Summarize the key findings
        2. Identify patterns in the results
        3. Suggest related searches or areas of interest
        4. Provide recommendations for further exploration
        """,
        expected_output="Analysis of search results with recommendations",
        agent=analytics
    )
    
    crew = Crew(
        agents=[db_manager, analytics],
        tasks=[search_task, analysis_task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew

def create_entity_update_workflow(entity_id: str, collection_name: str, update_data: str):
    """Create a workflow for updating existing entity information."""
    
    db_manager = create_database_manager_agent()
    analytics = create_analytics_agent()
    
    update_task = Task(
        description=f"""
        Update entity {entity_id} in collection {collection_name} with new information:
        
        {update_data}
        
        1. Retrieve the current entity information
        2. Merge the new data appropriately
        3. Update relationships if needed
        4. Verify the update was successful
        """,
        expected_output="Confirmation of update with before/after comparison",
        agent=db_manager
    )
    
    impact_analysis_task = Task(
        description="""
        Analyze the impact of the entity update:
        
        1. Check how the update affects related entities
        2. Identify any new relationships created
        3. Suggest additional updates that might be needed
        4. Verify data consistency
        """,
        expected_output="Impact analysis report with recommendations",
        agent=analytics
    )
    
    crew = Crew(
        agents=[db_manager, analytics],
        tasks=[update_task, impact_analysis_task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew

# === EXAMPLE USAGE ===

def test_entity_management_system():
    """Test the complete entity management system."""
    
    # Sample text with various entities
    sample_text = """
    I had a productive meeting with Sarah Johnson, the CTO of TechStart Inc., 
    yesterday at their San Francisco office. We discussed the AI Integration Project 
    which is scheduled to launch in Q2 2024. Sarah mentioned they need help with 
    machine learning model deployment on AWS.
    
    Action items from the meeting:
    - Send proposal by Friday, March 15th
    - Schedule technical review with their engineering team
    - Prepare demo for next Tuesday at 2 PM
    
    Sarah's contact info: sarah.johnson@techstart.com, (415) 555-0123
    
    The project involves integrating LLM capabilities into their customer service 
    platform. Budget is around $150,000 for the initial phase.
    """
    
    print("🚀 Testing Entity Management System")
    print("=" * 50)
    
    # Create and run extraction workflow
    extraction_crew = create_entity_extraction_workflow(sample_text)
    
    print("📊 Running entity extraction workflow...")
    extraction_result = extraction_crew.kickoff()
    
    print("\n" + "="*50)
    print("📝 EXTRACTION WORKFLOW RESULT:")
    print("="*50)
    print(extraction_result)
    
    # Test search workflow
    print("\n🔍 Testing search workflow...")
    search_crew = create_entity_search_workflow("Sarah Johnson", "people")
    search_result = search_crew.kickoff()
    
    print("\n" + "="*50)
    print("🔍 SEARCH WORKFLOW RESULT:")
    print("="*50)
    print(search_result)

def create_smart_assistant_agent():
    """Create a smart assistant that can handle any entity-related request."""
    return Agent(
        role="Smart Entity Assistant",
        goal="Help users manage their information by extracting, storing, searching, and analyzing entities",
        backstory="""You are an intelligent assistant specializing in information management. 
        You can help users extract important information from text, organize it in a searchable 
        database, and provide insights about their data. You understand the relationships 
        between different types of information and can help users find what they need quickly.""",
        llm="ollama/qwen2.5",  # Best overall reasoning
        tools=ENTITY_TOOLS,
        verbose=True,
        allow_delegation=False
    )

def handle_user_request(user_input: str):
    """Handle any user request related to entity management."""
    
    assistant = create_smart_assistant_agent()
    
    task = Task(
        description=f"""
        User request: "{user_input}"
        
        Analyze what the user wants and take appropriate action:
        
        1. If they provide text to analyze, extract entities and store them
        2. If they want to search for information, search the database
        3. If they want to update information, help them update entities
        4. If they want insights, provide analysis and trends
        
        Always be helpful and explain what you're doing and why.
        """,
        expected_output="Complete response to the user's request with detailed explanations",
        agent=assistant
    )
    
    crew = Crew(
        agents=[assistant],
        tasks=[task],
        verbose=True
    )
    
    return crew.kickoff()

if __name__ == "__main__":
    # Run the test
    test_entity_management_system()