# Mistral AI Test Project

This project provides a scaffold for testing Mistral AI services. All development and examples have been created using **Mistral AI Vibe CLI 2.2.1** and the **Devstral 2** model.

**Powered by:**
- 🤖 Mistral AI Vibe CLI 2.2.1
- 🧠 Devstral 2 Model

## Features

- Python 3.12+ environment with venv
- **Mistral AI Vibe CLI 2.2.1** integration with determinism control
- **Devstral 2** model support
- Git version control
- Environment variable management with python-dotenv
- Code formatting with Black
- Linting with Ruff
- Type checking with mypy
- Testing with pytest
- Determinism controller for precise AI response control
- **Streaming responses** for real-time output
- **Performance metrics** tracking (tokens, duration, etc.)
- Comprehensive error handling and validation
- Multiple response modes (regular, streaming, with metrics)
- **Standardized output** with colorama for better UX
- **Batch processing** with JSONL format support

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MistalAITests.git
   cd MistalAITests
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Mistral AI API key
   ```

## Usage

Run tests:
```bash
pytest
```

Format code:
```bash
black .
```

Lint code:
```bash
ruff check .
```

Type check:
```bash
mypy .
```

Run example with determinism control:
```bash
python src/example_determinism.py
```

## New Features

### Streaming Responses

Get real-time responses chunk by chunk:

```python
from src.mistral_client import MistralAIClient

client = MistralAIClient(api_key="your_api_key")
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Tell me a story about AI."}
]

print("Streaming response:")
for chunk in client.chat_completion_stream(messages):
    print(chunk, end='', flush=True)
```

### Performance Metrics

Get detailed metrics about your API calls:

```python
result = client.chat_completion_with_metrics(messages)
print(f"Response: {result['content']}")
print(f"Duration: {result['duration']:.3f} seconds")
print(f"Tokens used: {result['tokens']['total']}")
print(f"Response time: {result['metrics']['response_time_ms']:.1f} ms")
```

### Enhanced Error Handling

```python
try:
    response = client.chat_completion([])  # Empty messages
except ValueError as e:
    print(f"Validation error: {e}")

try:
    response = client.chat_completion(messages)
except RuntimeError as e:
    print(f"API error: {e}")
```

## Project Structure

```
MistalAITests/
├── .venv/                     # Virtual environment
├── .git/                      # Git repository
├── .gitignore                 # Git ignore rules
├── .env                       # Environment variables
├── .env.example               # Example environment variables
├── src/                       # Source code
│   ├── __init__.py
│   ├── mistral_client.py      # Mistral AI client
│   ├── determinism_controller.py # Determinism control
│   └── utils.py               # Utilities
├── tests/                     # Tests
│   ├── __init__.py
│   └── test_mistral.py        # Test cases
├── README.md                  # Documentation
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
└── pyproject.toml             # Project configuration
```

## Project Information

**Developer:** David R. Lopez B.
**Email:** ibitato@gmail.com
**Tools:** OpenCode 1.1.35 with Devstral 2 Medium LLM

## Determinism Control

This project includes a determinism controller that allows fine-grained control over AI response creativity vs. precision:

- **Level 1 (Exact):** Deterministic responses, minimal variation
- **Level 2 (Focused):** Highly controlled generation, minimal creativity  
- **Level 3 (Balanced):** Balanced generation (default)
- **Level 4 (Creative):** More freedom and variation
- **Level 5 (Free):** Highly creative, maximum variation

The determinism controller automatically handles Mistral AI requirements, such as setting `top_p=1.0` when using greedy sampling (`temperature=0.0`).

## 🎯 Development Credits

This project and all examples were developed using:

**Mistral AI Vibe CLI 2.2.1** - The powerful CLI tool that enabled rapid development and testing of Mistral AI services.

**Devstral 2 Model** - The advanced language model that powers all the AI responses and demonstrations in this project.

### About Mistral AI

Mistral AI provides state-of-the-art language models and tools for building intelligent applications. This project demonstrates best practices for integrating with Mistral AI services using their official Python SDK and CLI tools.

### Development Environment

- **CLI Tool**: Mistral AI Vibe CLI 2.2.1
- **Model**: Devstral 2
- **SDK**: mistralai Python package
- **Framework**: Python 3.12+

### Developer

**David R. Lopez B.**
- Email: ibitato@gmail.com
- GitHub: [davidlopezb](https://github.com/davidlopezb)
- Role: Lead Developer & Architect

## License

MIT