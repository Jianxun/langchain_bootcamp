# LangChain Bootcamp

## Description
Brief description of your project.

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Available Tools

### LLM API
Interact with various LLM providers:
```bash
python tools/llm_api.py --prompt "Your prompt" --provider {openai|anthropic|gemini|azure|deepseek|local}
```

### Screenshot Utils
Capture and analyze web screenshots:
```bash
python tools/screenshot_utils.py URL --output screenshot.png
```

### Web Scraper
Scrape content from web pages:
```bash
python tools/web_scraper.py --max-concurrent 3 URL1 URL2 URL3
```

### Search Engine
Search the web using DuckDuckGo:
```bash
python tools/search_engine.py "your search query"
```

## Project Documentation
Project documentation is maintained in the Obsidian vault under:
`/Projects/[project_name]/context.md`

## Contributing
1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request

## License
[Your chosen license] 