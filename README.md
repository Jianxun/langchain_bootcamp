# LangChain Bootcamp

A comprehensive learning project for building practical applications using LangChain. This project covers various aspects of LangChain and LLM application development through hands-on examples and exercises.

## Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the project root with your API keys:

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Azure OpenAI (if using)
AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_ENDPOINT=your_azure_endpoint_here
AZURE_OPENAI_MODEL_DEPLOYMENT=your_model_deployment_name

# Optional: Anthropic (if using)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: DeepSeek (if using)
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## Running the Applications

### Day 1: LangChain Fundamentals

```bash
# Run the basic chatbot
python day1/basic_chat.py

# Run the Streamlit chat interface
streamlit run day1/chat_app.py
```

### Day 2: Advanced Prompting and Chains

```bash
# Run the text summarizer
python day2/summarizer.py

# Run the Streamlit summarizer interface
streamlit run day2/summarizer_app.py
```

### Day 3: RAG (Retrieval Augmented Generation)

```bash
# Run the document Q&A system
python day3/rag_system.py

# Run the Streamlit document Q&A interface
streamlit run day3/rag_app.py
```


## Available Tools

### Search Engine
```bash
# Search the web
python tools/search_engine.py "your search query"
```

### Web Scraper
```bash
# Scrape web content
python tools/web_scraper.py --max-concurrent 3 URL1 URL2 URL3
```

## Learning Plan

The project follows a structured learning plan covering:

- [x] Day 1: LangChain Fundamentals
   - Basic concepts
   - LLM integration
   - Prompt templates
   - Basic chains

- [x] Day 2: Advanced Prompting and Chains
   - Different types of prompts
   - Chain types and patterns
   - Text summarization project

- [x] Day 3: RAG (Retrieval Augmented Generation)
   - Document processing
   - Embeddings
   - Document Q&A system

- [ ] Day 4: Agents and Tools
   - Agent types
   - Tool integration
   - AI Assistant implementation

- [ ] Day 5: Memory and Context
   - Memory types
   - Context management
   - Enhanced chatbot

- [ ] Day 6: Advanced Workflows
   - Complex chains
   - External integration
   - Research assistant

- [ ] Day 7: Deployment and Production
   - Application deployment
   - Production considerations
   - Web application deployment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Streamlit Documentation](https://docs.streamlit.io/) 