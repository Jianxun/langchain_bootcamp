# Day 1: LangChain Fundamentals

## Learning Objectives
1. Core LangChain Concepts
   - LLM (Language Model) integration
   - Prompt Templates and their importance
   - Basic Chains and how they work
   - Environment setup and configuration

2. Experiment with different parameters:
   - Temperature and its effect on responses
   - Max tokens and response length
   - Different model options (GPT-3.5 vs GPT-4)

## Key Concepts

### LLM Integration
- Using `langchain-openai` for OpenAI integration
- ChatOpenAI vs OpenAI models
- Model parameters and configuration

### Prompt Templates
- Basic templates
- Chat templates
- Different styles and formats

### Basic Chains
- Chain composition
- Pipe operator pattern
- Input/output handling

## Running the Applications

### Command Line Chatbot
To run the command line version:
```bash
python day1_simple_chatbot.py
```

### Streamlit Web App
To run the web interface version:
```bash
streamlit run day1_simple_chatbot_app.py
```

The Streamlit app provides:
- A dropdown menu to select conversation styles
- A modern chat interface
- Persistent chat history
- Clear chat functionality
- Helpful sidebar with information

## Project Structure
```
day1/
├── day1_simple_chatbot.py      # Command line chatbot
├── day1_simple_chatbot_app.py  # Streamlit web interface
└── README.md                   # This file
```

## Dependencies
Make sure you have the required packages installed:
```bash
pip install -r requirements.txt
```

## Environment Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables in `.env`:
```
OPENAI_API_KEY=your_api_key_here
``` 