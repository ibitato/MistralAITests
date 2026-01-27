# Mistral AI Test Project

This project provides a scaffold for testing Mistral AI services using the official Python SDK.

## Features

- Python 3.12+ environment with venv
- Mistral AI SDK integration with determinism control
- Git version control
- Environment variable management with python-dotenv
- Code formatting with Black
- Linting with Ruff
- Type checking with mypy
- Testing with pytest
- Determinism controller for precise AI response control

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
python example_usage.py
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

The determinism controller automatically handles Mistral API requirements, such as setting `top_p=1.0` when using greedy sampling (`temperature=0.0`).

## License

MIT