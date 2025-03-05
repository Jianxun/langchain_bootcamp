# Day 1: Simple LLM-Powered Chatbot

This project implements a basic chatbot using LangChain and OpenAI's GPT models. It demonstrates fundamental LangChain concepts including:
- LLM initialization and configuration
- Prompt templates
- Basic chains

## Setup

1. Make sure you have Python 3.8+ installed
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the parent directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the chatbot:
```bash
python simple_chatbot.py
```

The chatbot will:
- Accept user input
- Generate responses using GPT-3.5-turbo
- Continue until you type 'quit'

## Key Concepts Demonstrated

- **LLM**: Using OpenAI's GPT model through LangChain
- **PromptTemplate**: Creating structured prompts for the LLM
- **LLMChain**: Combining prompts and LLM into a workflow
- **Environment Variables**: Managing API keys securely

## Customization

You can modify the following parameters in `simple_chatbot.py`:
- `temperature`: Controls response randomness (0.0 to 1.0)
- `max_tokens`: Maximum length of responses
- `model_name`: The GPT model to use 