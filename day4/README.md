# Day 4: Agents and Tools

## Overview
Day 4 focuses on implementing AI agents that can use tools to accomplish complex tasks. We'll explore different types of agents, tool integration patterns, and build an AI assistant capable of using multiple tools effectively.

## Key Components

### 1. Agent Types
- **ReAct Agents**: Agents that follow the Reasoning and Acting pattern
  - Observation-thought-action cycle
  - Step-by-step reasoning
  - Dynamic tool selection
- **Plan-and-Execute Agents**: Agents that plan before taking action
  - Task decomposition
  - Strategy formulation
  - Sequential execution
- **Custom Agents**: Building specialized agents for specific tasks
  - Custom reasoning patterns
  - Domain-specific behaviors
  - Specialized tool usage

### 2. Tool Integration
- **Built-in Tools**: Using LangChain's standard tools
  - Web search
  - Calculator
  - Shell commands
  - File operations
- **Custom Tools**: Creating task-specific tools
  - Tool definition
  - Input/output handling
  - Error management
- **Tool Selection**: Implementing smart tool choice
  - Context-aware selection
  - Tool prioritization
  - Fallback strategies

## Project: Multi-Tool AI Assistant

### Features
- Multiple tool integration
- Dynamic tool selection
- Step-by-step reasoning
- Interactive interface
- Error handling and recovery

### Technical Implementation
1. **Agent Setup**:
   ```python
   from langchain.agents import AgentType, initialize_agent
   from langchain.tools import Tool
   
   # Define tools
   tools = [
       Tool(
           name="Search",
           func=search_tool.run,
           description="Useful for searching the web"
       ),
       Tool(
           name="Calculator",
           func=calculator_tool.run,
           description="Useful for mathematical calculations"
       )
   ]
   
   # Initialize agent
   agent = initialize_agent(
       tools,
       llm,
       agent=AgentType.REACT_DOCSTORE,
       verbose=True
   )
   ```

2. **Custom Tool Creation**:
   ```python
   class CustomTool(BaseTool):
       name = "custom_tool"
       description = "Description of what this tool does"
       
       def _run(self, query: str) -> str:
           # Tool implementation
           return result
           
       def _arun(self, query: str) -> str:
           # Async implementation
           return result
   ```

3. **Agent Execution**:
   ```python
   # Run agent with a task
   result = agent.run(
       "What is the weather in London and what's 2+2?"
   )
   ```

### User Interface
- Task input field
- Reasoning display
- Tool usage tracking
- Results presentation
- Error messages and recovery options

## Learning Outcomes
1. Understanding different agent types and their use cases
2. Implementing and integrating tools
3. Building custom agents and tools
4. Managing complex task execution
5. Handling errors and edge cases

## Next Steps
1. Enhance the assistant with:
   - More specialized tools
   - Better error recovery
   - Advanced planning capabilities
   - Memory integration
2. Improve the interface with:
   - Visual tool selection
   - Execution monitoring
   - Debug information
   - Performance metrics

## Running the Application
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   OPENAI_API_KEY=your_api_key_here
   ```

3. Run the application:
   ```bash
   streamlit run day4/agent_assistant_app.py
   ```

## Project Structure
```
day4/
├── agent_assistant_app.py  # Main Streamlit application
├── tools/                  # Custom tools directory
│   ├── __init__.py
│   ├── search_tool.py     # Web search tool
│   ├── calculator_tool.py # Calculator tool
│   └── custom_tools.py    # Additional custom tools
├── agents/                # Agent implementations
│   ├── __init__.py
│   ├── react_agent.py    # ReAct agent implementation
│   └── planner_agent.py  # Plan-and-execute agent
└── README.md             # This file
``` 