"""
Step 3: Building an Agent Team - Delegation for Greetings & Farewells
Main executable file with API keys configuration
"""

import asyncio
import os
from google.adk import Agent, Runner
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import tools and agents from the separate file
from step3_agents import get_weather, greeting_agent, farewell_agent

# ============================================================================
# API KEYS CONFIGURATION - Replace with your actual API keys
# ============================================================================
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================
MODEL_GEMINI_2_5_FLASH = "gemini-2.5-flash"  # Default Gemini model

# ============================================================================
# HELPER FUNCTION FOR AGENT CALLS
# ============================================================================
async def call_agent_async(query: str, runner: Runner, user_id: str, session_id: str):
    """
    Helper function to call an agent and print its response.
    
    Args:
        query: The user's query string
        runner: The Runner instance to use
        user_id: User identifier for the session
        session_id: Session identifier
    """
    print(f"\n{'='*60}")
    print(f"User Query: {query}")
    print(f"{'='*60}")
    
    # Run the agent through the runner
    response_text = ""
    # Convert query string to types.Content
    content = types.Content(parts=[types.Part(text=query)])
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text
    
    # Print the agent's response
    print(f"\nAgent Response:\n{response_text}")
    print(f"{'-'*60}\n")


# ============================================================================
# ROOT AGENT DEFINITION
# ============================================================================
def create_root_agent():
    """
    Creates the root agent (weather_agent_team) with sub-agents.
    
    The root agent coordinates a team of specialized agents:
    - greeting_agent: Handles greetings
    - farewell_agent: Handles farewells
    - get_weather tool: Handles weather requests directly
    """
    root_agent = Agent(
        name="weather_agent_v2",
        model=MODEL_GEMINI_2_5_FLASH,
        description="The main coordinator agent. Handles weather requests and delegates greetings/farewells to specialists.",
        instruction=(
            "You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information. "
            "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
            "You have specialized sub-agents: "
            "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
            "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
            "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
            "If it's a weather request, handle it yourself using 'get_weather'. "
            "For anything else, respond appropriately or state you cannot handle it."
        ),
        tools=[get_weather],  # Root agent retains weather tool for direct handling
        sub_agents=[greeting_agent, farewell_agent]  # Link specialized sub-agents
    )
    
    print(f"✅ Root Agent '{root_agent.name}' created using model '{MODEL_GEMINI_2_5_FLASH}'")
    print(f"   Sub-agents: {[sa.name for sa in root_agent.sub_agents]}")
    
    return root_agent


# ============================================================================
# MAIN CONVERSATION FUNCTION
# ============================================================================
async def run_team_conversation():
    """
    Demonstrates the agent team delegation mechanism.
    
    Tests three types of queries:
    1. Greeting - delegated to greeting_agent
    2. Weather request - handled by root agent
    3. Farewell - delegated to farewell_agent
    """
    print("\n" + "="*60)
    print("TESTING AGENT TEAM DELEGATION")
    print("="*60)
    
    # Create a dedicated session service for this conversation
    session_service = InMemorySessionService()
    
    # Define session identifiers
    APP_NAME = "weather_tutorial_agent_team"
    USER_ID = "user_1_agent_team"
    SESSION_ID = "session_001_agent_team"
    
    # Create the session
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"\n✅ Session created:")
    print(f"   App: '{APP_NAME}'")
    print(f"   User: '{USER_ID}'")
    print(f"   Session: '{SESSION_ID}'")
    
    # Create the root agent
    root_agent = create_root_agent()
    
    # Create runner for the root agent
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"\n✅ Runner created for agent '{root_agent.name}'")
    
    # Test interactions
    print("\n" + "="*60)
    print("INTERACTION 1: GREETING (should delegate to greeting_agent)")
    print("="*60)
    await call_agent_async(
        query="Hello there! my name is srineesh",
        runner=runner,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    print("\n" + "="*60)
    print("INTERACTION 2: WEATHER REQUEST (handled by root agent)")
    print("="*60)
    await call_agent_async(
        query="What is the weather in New York?",
        runner=runner,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    print("\n" + "="*60)
    print("INTERACTION 3: FAREWELL (should delegate to farewell_agent)")
    print("="*60)
    await call_agent_async(
        query="Thanks, bye!",
        runner=runner,
        user_id=USER_ID,
        session_id=SESSION_ID
    )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("AGENT TEAM TUTORIAL - STEP 3")
    print("="*60)
    print("\nExecuting agent team conversation using asyncio.run()...")
    
    try:
        asyncio.run(run_team_conversation())
        print("\n" + "="*60)
        print("✅ AGENT TEAM CONVERSATION COMPLETED SUCCESSFULLY")
        print("="*60)
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ AN ERROR OCCURRED: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
