# LangChain Bootcamp Project Context

## Project Overview
This is a learning project focused on building practical applications using LangChain. The project follows a structured learning plan covering various aspects of LangChain and LLM application development.

## Current Progress
We are currently on Day 4 of the learning plan, focusing on Agents and Tools implementation.

### Latest Implementation
- Working on Plan and Execute Agent in `day4/agents/planner_agent.py`
- Implemented tools:
  - `SearchTool`: Web search with Wikipedia integration
  - `LookupTool`: Mathematical calculations using LLMMathChain

### Recent Changes
1. Fixed imports to use correct LangChain packages:
   - Using `langchain_core.tools.BaseTool`
   - Using `langchain_core.language_models.base.BaseLanguageModel`
2. Improved number handling in calculations
3. Enhanced plan execution with better error handling

### Environment Setup
- Python virtual environment in `./venv`
- Key dependencies:
  - langchain
  - langchain-openai
  - numexpr (required for LLMMathChain)
- Using OpenAI's "gpt-4o" model as default

## Key Lessons Learned
1. Package Management:
   - Use `langchain-community` for third-party integrations
   - Use `langchain_core` for base classes
   - Use `langchain-openai` for OpenAI specific functionality

2. Model Configuration:
   - Use "gpt-4o" as the model name for OpenAI's GPT-4
   - Set appropriate temperature (0 for deterministic tasks)

3. Best Practices:
   - Include debug information in stderr
   - Keep main output clean in stdout
   - Implement proper error handling and fallbacks
   - Use dynamic creation of API wrappers to avoid Pydantic validation issues

## Current Task Status
### Completed
- [X] ReAct agents implementation
- [X] Basic tool integration
- [X] Search and calculation capabilities
- [X] Error handling and recovery

### In Progress
- [ ] Plan-and-execute agents completion
- [ ] Custom agents development
- [ ] User interface for tool interaction

## Next Steps
1. Complete Plan-and-execute agents implementation
2. Develop custom agents for specific use cases
3. Create user interface for tool interaction
4. Add more specialized tools based on needs

## File Structure
Key files:
- `day4/agents/planner_agent.py`: Main agent implementation
- `tools/search_engine.py`: Web search functionality
- `tools/web_scraper.py`: Web content extraction
- `.cursorrules`: Project rules and progress tracking

## Dependencies
Required packages:
```
langchain
langchain-openai
langchain-community
numexpr
python-dotenv
requests
beautifulsoup4
```

## Environment Variables
Required in `.env`:
- `OPENAI_API_KEY`: OpenAI API key
- Other API keys as needed for additional services

## Known Issues
- Need to handle large numbers in calculations more effectively
- Need to improve number extraction from search results
- Plan execution could be more robust with retries

## Future Improvements
1. Add retry mechanisms for failed API calls
2. Implement better number parsing from text
3. Add more sophisticated error recovery
4. Create a more user-friendly interface

## Resources
- LangChain Documentation
- OpenAI API Documentation
- Project Learning Plan (in `.cursorrules`) 