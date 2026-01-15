"""
Step 3: Tools and Agent Definitions
Contains all tool functions and specialized agent definitions
"""

from typing import Optional
from google.adk import Agent

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================
MODEL_GEMINI_2_5_FLASH = "gemini-2.0-flash"

# ============================================================================
# MOCK WEATHER DATABASE
# ============================================================================
# Simple dictionary simulating a weather data source
MOCK_WEATHER_DB = {
    "London": {"temperature": 15, "condition": "Cloudy"},
    "New York": {"temperature": 22, "condition": "Sunny"},
    "Tokyo": {"temperature": 18, "condition": "Rainy"},
    "Paris": {"temperature": 12, "condition": "Windy"},
    "Sydney": {"temperature": 25, "condition": "Clear"},
}


# ============================================================================
# WEATHER TOOL (From Step 1)
# ============================================================================
def get_weather(city: str) -> dict:
    """
    Retrieves weather information for a given city.
    
    This tool looks up weather data from a mock database and returns
    the current weather conditions for the specified city.
    
    Args:
        city (str): The name of the city to get weather for (e.g., "London", "Tokyo").
    
    Returns:
        dict: A dictionary with keys:
            - "status" (str): "success" or "error"
            - "report" (str): Weather report (if success)
            - "error_message" (str): Error description (if error)
    """
    print(f"--- Tool: get_weather called with city: {city} ---")
    
    # Normalize city name for lookup (capitalize first letter)
    city_normalized = city.strip().title()
    
    # Check if city exists in mock database
    if city_normalized in MOCK_WEATHER_DB:
        weather_data = MOCK_WEATHER_DB[city_normalized]
        report = (
            f"The weather in {city_normalized} is currently "
            f"{weather_data['condition'].lower()} with a temperature "
            f"of {weather_data['temperature']}°C."
        )
        return {"status": "success", "report": report}
    else:
        return {
            "status": "error",
            "error_message": f"Weather data for '{city}' is not available in the database."
        }


# ============================================================================
# GREETING TOOL
# ============================================================================
def say_hello(name: Optional[str] = None) -> str:
    """
    Provides a simple greeting. If a name is provided, it will be used.
    
    This tool generates a friendly greeting message, optionally personalized
    with the user's name if provided.
    
    Args:
        name (str, optional): The name of the person to greet. 
                             Defaults to a generic greeting if not provided.
    
    Returns:
        str: A friendly greeting message.
    """
    if name:
        greeting = f"Hello, {name}!"
        print(f"--- Tool: say_hello called with name: {name} ---")
    else:
        greeting = "Hello there!"
        print(f"--- Tool: say_hello called without a specific name (name_arg_value: {name}) ---")
    
    return greeting


# ============================================================================
# FAREWELL TOOL
# ============================================================================
def say_goodbye() -> str:
    """
    Provides a simple farewell message to conclude the conversation.
    
    This tool generates a polite goodbye message when the user is
    ending the conversation.
    
    Returns:
        str: A farewell message.
    """
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."


# ============================================================================
# GREETING AGENT (Specialized Sub-Agent)
# ============================================================================
greeting_agent = Agent(
    name="greeting_agent",
    model=MODEL_GEMINI_2_5_FLASH,
    instruction=(
        "You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
        "Use the 'say_hello' tool to generate the greeting. "
        "If the user provides their name, make sure to pass it to the tool. "
        "Do not engage in any other conversation or tasks."
    ),
    description="Handles simple greetings and hellos using the 'say_hello' tool.",
    tools=[say_hello],
)

print(f"✅ Agent '{greeting_agent.name}' created using model '{greeting_agent.model}'")


# ============================================================================
# FAREWELL AGENT (Specialized Sub-Agent)
# ============================================================================
farewell_agent = Agent(
    name="farewell_agent",
    model=MODEL_GEMINI_2_5_FLASH,
    instruction=(
        "You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
        "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
        "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
        "Do not perform any other actions."
    ),
    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
    tools=[say_goodbye],
)

print(f"✅ Agent '{farewell_agent.name}' created using model '{farewell_agent.model}'")
