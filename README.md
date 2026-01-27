# Mistral AI Test Project

This project provides a scaffold for testing Mistral AI services using the official Python SDK.

## Features

- Python 3.12+ environment with venv
- Mistral AI SDK integration
- Git version control
- Environment variable management with python-dotenv
- Code formatting with Black
- Linting with Ruff
- Type checking with mypy
- Testing with pytest

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
│   └── utils.py               # Utilities
├── tests/                     # Tests
│   ├── __init__.py
│   └── test_mistral.py        # Test cases
├── README.md                  # Documentation
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
└── pyproject.toml             # Project configuration
```

## License

MIT