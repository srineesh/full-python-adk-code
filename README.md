# Google ADK Learning Journey

Welcome to my **Google Agent Development Kit (ADK)** learning repository!

## 🎯 Goal
My goal for this repository is to document my daily learning progress with Google ADK. While the [official documentation](https://google.github.io/adk-docs/) often presents code in smaller chunks, I aim to create **single, consolidated Python executable files** for each concept and tutorial step. This makes it easier to run, test, and understand the full flow of the agents.

## 📂 Repository Structure

The repository is organized by tutorials and concepts.

- **`agent_team/`**: Contains code from the "Agent Team" tutorial series.
  - [`step1-weather_agent_demo.py`](agent_team/step1-weather_agent_demo.py): **Step 1: Basic Weather Lookup**. A single-file implementation of the basic weather agent that defines the tool, agent, session, and runner in one script.
  - [`step2-weather_agent_with_fallback.py`](agent_team/step2-weather_agent_with_fallback.py): **Step 2**. Implementation of the weather agent with model fallback capabilities.
  - (More steps to be added daily!)

- **`multi_tool_agent/`**: Experiments with multi-tool agents.

## 🚀 Getting Started

### Prerequisites

1.  **Python 3.9+**
2.  **Google ADK** installed:
    ```bash
    pip install google-adk
    ```
3.  **API Keys**: Ensure you have your Google Cloud Project set up and API keys ready (e.g., `GOOGLE_API_KEY`). You can set these in a `.env` file or export them in your terminal.

### Running the Examples

Since these are self-contained scripts, you can run them directly with Python.

**Example: Run Step 1**
```bash
python agent_team/step1-weather_agent_demo.py
```

This will execute the agent flow, usually printing the interaction steps to the console.

## 📅 Progress

I plan to update this repository daily as I work through the ADK documentation and build more complex agents.

---
*Created as part of my daily learning log.*
