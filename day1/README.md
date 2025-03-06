# Day 1: LangChain Fundamentals

## Overview
Day 1 introduces the core concepts of LangChain and implements a basic chatbot using OpenAI's language models. The focus is on understanding the fundamental components of LangChain and how they work together.

## Key Components

### 1. Language Models
- **OpenAI Integration**: Using `ChatOpenAI` from LangChain for chat-based interactions
- **Model Configuration**: Understanding temperature and other model parameters
- **Response Handling**: Processing and formatting model outputs

### 2. Prompt Templates
- **Basic Templates**: Creating simple text templates for model inputs
- **Chat Templates**: Implementing structured chat message templates
- **Template Variables**: Managing dynamic content in prompts

### 3. Chains
- **Basic Chains**: Understanding the chain concept in LangChain
- **Pipe Operator Pattern**: Using modern `prompt | llm` syntax
- **Chain Execution**: Managing chain inputs and outputs

## Project: Simple Chatbot

### Features
- Interactive chat interface
- Configurable model parameters
- Multiple chat styles
- Streamlit-based user interface

### Technical Implementation
1. **Model Setup**:
   ```python
   llm = ChatOpenAI(
       model="gpt-3.5-turbo",
       temperature=0.7
   )
   ```

2. **Prompt Template**:
   ```python
   prompt = ChatPromptTemplate.from_messages([
       ("system", "You are a helpful assistant."),
       ("human", "{input}")
   ])
   ```

3. **Chain Creation**:
   ```python
   chain = prompt | llm
   response = chain.invoke({"input": user_input})
   ```

### User Interface
- Chat style selector
- Message input field
- Chat history display
- Parameter controls in sidebar:
  - Temperature
  - Model selection
  - Max tokens

## Learning Outcomes
1. Understanding LangChain's core components
2. Working with OpenAI's chat models
3. Creating and using prompt templates
4. Building basic chains
5. Developing interactive chat applications

## Next Steps
1. Enhance the chatbot with:
   - Memory and context management
   - Different conversation styles
   - Error handling
   - Rate limiting
2. Improve the interface with:
   - Message threading
   - User preferences
   - Export functionality
   - Theme customization

## Running the Application
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - Create a `.env` file with your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

3. Run the Streamlit app:
   ```bash
   streamlit run day1/simple_chatbot_app.py
   ```

4. Start chatting with the AI assistant!

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