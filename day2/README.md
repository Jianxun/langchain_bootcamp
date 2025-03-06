# Day 2: Advanced Prompting and Chains

## Overview
Day 2 explores advanced prompting techniques and complex chain patterns in LangChain, culminating in the development of a flexible document summarizer that can generate summaries in multiple styles.

## Key Components

### 1. Advanced Prompting
- **Few-shot Learning**: Implementing example-based prompting
  - Example selection strategies
  - Impact of example size
  - Dynamic example generation
- **Chain of Thought**: Building reasoning chains
  - Step-by-step problem solving
  - Different problem types
  - Few-shot chain of thought

### 2. Chain Patterns
- **Sequential Chains**: Building multi-step workflows
  - Data flow between steps
  - Error handling
  - State management
- **Parallel Chains**: Running multiple chains simultaneously
  - Concurrent execution
  - Result aggregation
  - Error handling
- **Branching Chains**: Implementing conditional logic
  - Path selection
  - Dynamic routing
  - Fallback handling

### 3. Chain Composition
- **Combined Patterns**: Mixing different chain types
  - Sequential with branching
  - Parallel with sequential
  - Complex workflows

## Project: Multi-style Document Summarizer

### Features
- Multiple summarization styles:
  - Bullet points
  - Narrative
  - Structured data (JSON)
- Configurable parameters
- Interactive interface
- Source text display

### Technical Implementation
1. **Style-specific Prompts**:
   ```python
   prompts = {
       "bullet": "Summarize the following text in bullet points:",
       "narrative": "Provide a narrative summary of the following text:",
       "json": "Summarize the following text in JSON format with key points:"
   }
   ```

2. **Chain Composition**:
   ```python
   # Create style-specific chain
   chain = prompt | llm
   
   # Execute with selected style
   response = chain.invoke({
       "style": selected_style,
       "text": input_text
   })
   ```

3. **Output Processing**:
   ```python
   # Format output based on style
   if style == "json":
       return json.loads(response)
   return response
   ```

### User Interface
- Style selector dropdown
- Input text area
- Summary output display
- Parameter controls in sidebar:
  - Temperature
  - Max tokens
  - Output format

## Learning Outcomes
1. Mastering advanced prompting techniques
2. Understanding chain patterns and composition
3. Building complex LangChain workflows
4. Implementing style-specific processing
5. Creating flexible document processing systems

## Next Steps
1. Enhance the summarizer with:
   - More summarization styles
   - Custom style templates
   - Batch processing
   - Export options
2. Improve the interface with:
   - Style preview
   - Format validation
   - Progress tracking
   - History management

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
   streamlit run day2/document_summarizer_app.py
   ```

4. Select a style and start summarizing! 