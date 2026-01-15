"""
Weather Agent with Model Fallback
Demonstrates automatic fallback from Gemini to OpenAI if Google API key fails
Tutorial link: https://google.github.io/adk-docs/tutorials/agent-team/#step-1-your-first-agent-basic-weather-lookup
Step 2: Going Multi-Model with LiteLLM [Optional]
"""

import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

import warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

# =============================================================================
# API KEY CONFIGURATION
# =============================================================================

# INTENTIONALLY WRONG Google API Key (to trigger fallback)
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"

# VALID OpenAI API Key (replace with your actual key)
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

# Configure ADK to use API keys directly (not Vertex AI)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

print("="*80)
print("API KEYS CONFIGURED")
print("="*80)
print(f"Google API Key: {os.environ['GOOGLE_API_KEY'][:20]}... (INTENTIONALLY INVALID)")
print(f"OpenAI API Key: {'SET ✓' if os.environ.get('OPENAI_API_KEY') != 'your_openai_api_key_here' else 'NOT SET - REPLACE IN CODE!'}")
print("="*80 + "\n")

# =============================================================================
# MODEL CONSTANTS
# =============================================================================

MODEL_GEMINI_2_5_FLASH = "gemini-2.5-flash"
MODEL_GPT_4O = "openai/gpt-4.1"  # Can also use: gpt-4.1-mini, gpt-4o, etc.

# =============================================================================
# STEP 1: Define the get_weather Tool
# =============================================================================

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")

    # Mock weather data
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}


# =============================================================================
# STEP 2: Create Agents with Different Models (with Fallback)
# =============================================================================

# List to store successfully created agents
available_agents = []

# Try to create Gemini agent (will fail due to invalid API key)
print("\n" + "="*80)
print("ATTEMPTING TO CREATE GEMINI AGENT...")
print("="*80)
try:
    weather_agent_gemini = Agent(
        name="weather_agent_gemini",
        model=MODEL_GEMINI_2_5_FLASH,
        description="Provides weather information using Gemini.",
        instruction="You are a helpful weather assistant. "
                    "When the user asks for the weather in a specific city, "
                    "use the 'get_weather' tool to find the information. "
                    "If the tool returns an error, inform the user politely. "
                    "If the tool is successful, present the weather report clearly.",
        tools=[get_weather],
    )
    available_agents.append(("Gemini", weather_agent_gemini))
    print(f"✓ Gemini agent created successfully!")
except Exception as e:
    print(f"✗ Failed to create Gemini agent: {str(e)[:100]}")
    print("  (This is expected with invalid Google API key)")

# Try to create OpenAI agent (should succeed)
print("\n" + "="*80)
print("ATTEMPTING TO CREATE OPENAI AGENT...")
print("="*80)
try:
    weather_agent_openai = Agent(
        name="weather_agent_openai",
        model=LiteLlm(model=MODEL_GPT_4O),
        description="Provides weather information using GPT-4.",
        instruction="You are a helpful weather assistant. "
                    "When the user asks for the weather in a specific city, "
                    "use the 'get_weather' tool to find the information. "
                    "If the tool returns an error, inform the user politely. "
                    "If the tool is successful, present the weather report clearly.",
        tools=[get_weather],
    )
    available_agents.append(("OpenAI GPT-4", weather_agent_openai))
    print(f"✓ OpenAI agent created successfully!")
except Exception as e:
    print(f"✗ Failed to create OpenAI agent: {str(e)[:100]}")
    print("  (Check your OpenAI API key!)")

# Check if we have at least one working agent
if not available_agents:
    print("\n" + "="*80)
    print("ERROR: NO AGENTS AVAILABLE")
    print("="*80)
    print("Both Gemini and OpenAI agents failed to initialize.")
    print("Please check your API keys and try again.")
    print("="*80)
    exit(1)

# =============================================================================
# STEP 3: Initialize Session Service and Runner
# =============================================================================

# Create session service to manage conversation state
session_service = InMemorySessionService()

# Define constants for identifying the interaction context
APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001"


async def init_session():
    """Initialize the session - must be called in async context."""
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
    return session

# Helper function to validate an agent
async def validate_agent(agent_name, agent):
    print(f"Validating agent: {agent_name}...")
    temp_session_service = InMemorySessionService()
    temp_runner = Runner(agent=agent, app_name="validator", session_service=temp_session_service)
    
    # Create a temporary session
    try:
        await temp_session_service.create_session(app_name="validator", user_id="check", session_id="test")
        
        # Simple "hello" checks connectivity
        content = types.Content(role='user', parts=[types.Part(text="Hello")])
        
        # We just need to ensure it doesn't raise an exception
        async for event in temp_runner.run_async(user_id="check", session_id="test", new_message=content):
            pass
            
        print(f"✓ Agent '{agent_name}' is valid and working.")
        return True
    except Exception as e:
        print(f"✗ Agent '{agent_name}' failed validation: {str(e)[:100]}...")
        return False

async def get_valid_runner(agents):
    """Iterates through agents and returns a runner for the first working one."""
    for model_name, agent in agents:
        if await validate_agent(model_name, agent):
            print(f"\n" + "="*80)
            print(f"SELECTED AGENT: {model_name}")
            print("="*80)
            print(f"Using agent: {agent.name}")
            print(f"Model: {model_name}")
            print("="*80 + "\n")
            
            # Create the real runner
            return Runner(
                agent=agent,
                app_name=APP_NAME,
                session_service=session_service
            )
            
    print("\n" + "="*80)
    print("CRITICAL ERROR: No agents passed validation.")
    print("="*80)
    return None


# =============================================================================
# STEP 4: Define Agent Interaction Function
# =============================================================================

async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."

    try:
        # Key Concept: run_async executes the agent logic and yields Events.
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            
            # Optional: Uncomment to see all events
            # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}")

            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate:
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                break

    except Exception as e:
        final_response_text = f"Error during agent execution: {str(e)[:100]}"

    print(f"<<< Agent Response: {final_response_text}")


# =============================================================================
# STEP 5: Run the Conversation
# =============================================================================

async def run_conversation():
    """Run the pre-programmed conversation with the agent."""
    
    # Initialize the session
    await init_session()
    
    # Get a valid runner (this performs the fallback check)
    runner = await get_valid_runner(available_agents)
    
    if not runner:
        print("Aborting conversation due to lack of valid agents.")
        return
    
    print("\n" + "="*80)
    print("STARTING CONVERSATION")
    print("="*80)
    
    await call_agent_async("What is the weather like in London?",
                          runner=runner,
                          user_id=USER_ID,
                          session_id=SESSION_ID)

    await call_agent_async("How about Paris?",
                          runner=runner,
                          user_id=USER_ID,
                          session_id=SESSION_ID)

    await call_agent_async("Tell me the weather in New York",
                          runner=runner,
                          user_id=USER_ID,
                          session_id=SESSION_ID)
    
    print("\n" + "="*80)
    print("CONVERSATION COMPLETE")
    print("="*80)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    """
    Execute the conversation using asyncio.run for standard Python script execution.
    """
    print("\n" + "="*80)
    print("WEATHER AGENT WITH MODEL FALLBACK")
    print("="*80)
    print("This script demonstrates automatic fallback:")
    print("1. Tries to create Gemini agent (will fail with invalid key)")
    print("2. Falls back to OpenAI GPT-4 agent (should succeed)")
    print("3. Uses whichever agent successfully initialized")
    print("="*80)
    
    try:
        asyncio.run(run_conversation())
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you replaced 'your_openai_api_key_here' with your actual OpenAI API key")
        print("2. Check that your OpenAI API key is valid")
        print("3. Verify you have internet connection")
