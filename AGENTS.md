# AGENTS.md - Guidelines for AI Agents in Mistral AI Test Project

This document provides comprehensive guidelines for AI agents (like opencode) operating in this Mistral AI test project repository.

## Important Project Rules

1. **Always use the virtual environment**: This project requires using the virtual environment for all Python operations. Always activate the venv before running any commands.
2. **Never use system Python**: Always use `python3` from the virtual environment, never the system Python.
3. **Follow the build commands**: Use the commands specified in the Build/Lint/Test Commands section below.

## Build/Lint/Test Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running Tests
```bash
# Run all tests with coverage
pytest tests/ -v

# Run a single test file
pytest tests/test_mistral.py -v

# Run a specific test
pytest tests/test_mistral.py::TestMistralAIClient::test_chat_completion -v

# Run tests with coverage report
pytest --cov=src --cov-report=term-missing
```

### Code Quality Tools
```bash
# Format code with Black
black .

# Run linting with Ruff
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Run type checking with mypy
mypy .

# Run all quality checks
black . && ruff check . && mypy .
```

### Common Development Commands
```bash
# Run example script
python example_usage.py

# Check Python version
python --version

# List installed packages
pip list

# Update pip
pip install --upgrade pip
```

## Code Style Guidelines

### Imports

1. **Import Order**: Follow PEP 8 import ordering
   - Standard library imports first
   - Third-party imports next
   - Local application imports last
   - Separate groups with blank lines

2. **Absolute vs Relative Imports**: Use absolute imports
   ```python
   # Good
   from src.mistral_client import MistralAIClient
   
   # Avoid
   from ..mistral_client import MistralAIClient
   ```

3. **Import Grouping**: Group related imports
   ```python
   from mistralai import Mistral
   from mistralai.models import UserMessage, AssistantMessage, SystemMessage
   ```

### Formatting

1. **Line Length**: Maximum 88 characters (configured in pyproject.toml)
2. **Indentation**: 4 spaces (no tabs)
3. **Spacing**: 
   - Two blank lines around top-level functions and classes
   - One blank line around method definitions
   - No spaces inside parentheses, brackets, or braces
4. **String Quotes**: Use double quotes for strings
5. **Trailing Commas**: Use trailing commas for multi-line constructs

### Type Annotations

1. **Function Signatures**: All functions must have complete type annotations
   ```python
   def validate_api_key(api_key: str | None) -> bool:
       """Validate Mistral AI API key format."""
       # ... implementation
   ```

2. **Union Types**: Use `X | Y` syntax (Python 3.10+)
   ```python
   # Good
   def format_message(role: str) -> UserMessage | AssistantMessage | SystemMessage:
       # ... implementation
   
   # Avoid (old syntax)
   from typing import Union
   def format_message(role: str) -> Union[UserMessage, AssistantMessage, SystemMessage]:
       # ... implementation
   ```

3. **Optional Types**: Use `X | None` instead of `Optional[X]`
   ```python
   # Good
   def process_data(data: str | None) -> Result | None:
       # ... implementation
   ```

### Naming Conventions

1. **Variables and Functions**: snake_case
   ```python
   api_key = "..."
   def validate_api_key(api_key: str) -> bool:
       # ... implementation
   ```

2. **Classes**: PascalCase
   ```python
   class MistralAIClient:
       # ... implementation
   ```

3. **Constants**: UPPER_SNAKE_CASE
   ```python
   MAX_RETRIES = 3
   DEFAULT_TIMEOUT = 30
   ```

4. **Private Members**: Leading underscore
   ```python
   class Client:
       def __init__(self):
           self._internal_state = None
   ```

### Error Handling

1. **Specific Exceptions**: Raise specific exceptions with descriptive messages
   ```python
   if not api_key:
       logger.error("API key is empty")
       raise ValueError("API key cannot be empty")
   ```

2. **Validation**: Validate inputs early
   ```python
   if role not in ["user", "assistant", "system"]:
       raise ValueError(f"Invalid role: {role}")
   ```

3. **Logging**: Use appropriate log levels
   ```python
   logger.error("API key is empty")
   logger.warning("API key may not be valid Mistral AI format")
   logger.info("Processing request")
   logger.debug("Detailed debugging information")
   ```

### Documentation

1. **Docstrings**: All public functions and classes must have Google-style docstrings
   ```python
   def chat_completion(
       self,
       messages: list[UserMessage | AssistantMessage | SystemMessage],
       temperature: float = 0.7,
   ) -> str:
       """Get chat completion from Mistral AI.

       Args:
           messages: List of chat messages
           temperature: Temperature for completion (0.0 to 1.0)

       Returns:
           Completion text
       """
       # ... implementation
   ```

2. **Module Docstrings**: Every module must have a module-level docstring
   ```python
   """
   Mistral AI Client Module

   This module provides a client for interacting with Mistral AI services.
   """
   ```

### Testing Guidelines

1. **Test Structure**: Use pytest with clear test class organization
   ```python
   class TestMistralAIClient:
       """Test cases for MistralAIClient class."""
       
       @pytest.fixture
       def mock_client(self):
           """Create a mock Mistral client."""
           with patch("src.mistral_client.Mistral") as mock:
               yield mock
   ```

2. **Test Naming**: Use descriptive test names
   ```python
   def test_chat_completion_with_valid_messages(self):
       """Test chat completion with valid messages."""
       # ... test implementation
   ```

3. **Mocking**: Use unittest.mock for external dependencies
   ```python
   with patch("src.mistral_client.Mistral") as mock:
       mock_instance = MagicMock()
       mock.return_value = mock_instance
       # ... test setup
   ```

### Project-Specific Guidelines

1. **Mistral AI Client Usage**: Always use the official Mistral client
   ```python
   from mistralai import Mistral
   from mistralai.models import UserMessage, AssistantMessage, SystemMessage
   
   client = Mistral(api_key=api_key)
   ```

2. **Environment Variables**: Use python-dotenv for configuration
   ```python
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   api_key = os.getenv("MISTRAL_AI_API_KEY")
   ```

3. **Message Formatting**: Use the provided utility functions
   ```python
   from src.utils import format_chat_message
   
   messages = [
       format_chat_message("system", "You are a helpful assistant"),
       format_chat_message("user", "Hello!")
   ]
   ```

### Git Guidelines

1. **Commit Messages**: Use conventional commits format
   ```
   feat: add new embedding functionality
   fix: correct API key validation
   docs: update README with usage examples
   test: add tests for chat completion
   refactor: improve error handling
   ```

2. **Branch Naming**: Use descriptive branch names
   ```
   feat/embedding-support
   fix/api-validation
   docs/usage-examples
   ```

3. **Pull Requests**: Include detailed description and reference issues

### Security Guidelines

1. **API Keys**: Never commit API keys or secrets
   - Use `.env` files (included in `.gitignore`)
   - Provide `.env.example` with placeholder values

2. **Error Messages**: Don't expose sensitive information in error messages

3. **Dependencies**: Regularly update dependencies for security patches

## Agent-Specific Instructions

### For opencode Agents

1. **Always check existing patterns** before implementing new functionality
2. **Follow the established code style** strictly
3. **Run all quality checks** before considering a task complete
4. **Write comprehensive tests** for any new functionality
5. **Document all public APIs** with proper docstrings
6. **Use the Mistral AI SDK** for all AI-related operations
7. **Handle errors gracefully** with appropriate logging

### Common Agent Tasks

1. **Adding new features**:
   - Create test cases first
   - Implement functionality
   - Update documentation
   - Run all quality checks

2. **Fixing bugs**:
   - Write reproduction test first
   - Implement fix
   - Verify all existing tests still pass
   - Update documentation if needed

3. **Refactoring**:
   - Ensure comprehensive test coverage
   - Make small, incremental changes
   - Maintain backward compatibility
   - Update documentation

## Project Structure

```
MistalAITests/
├── .venv/                     # Virtual environment
├── .git/                      # Git repository
├── .gitignore                 # Git ignore rules
├── .env                       # Environment variables (NOT committed)
├── .env.example               # Example environment variables
├── src/                       # Source code
│   ├── __init__.py
│   ├── mistral_client.py      # Mistral AI client
│   └── utils.py               # Utilities
├── tests/                     # Tests
│   ├── __init__.py
│   └── test_mistral.py        # Test cases
├── example_usage.py           # Example script
├── README.md                  # Documentation
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
└── pyproject.toml             # Project configuration
```

## Best Practices

1. **Keep functions small and focused** - Single responsibility principle
2. **Write pure functions** when possible - Easier to test and reason about
3. **Use type hints** consistently - Improves code clarity and IDE support
4. **Document assumptions** in docstrings - Helps future maintainers
5. **Handle edge cases** explicitly - Don't rely on implicit behavior
6. **Write tests first** when possible - Test-driven development approach
7. **Run quality tools frequently** - Catch issues early

## Troubleshooting

1. **Import errors**: Check virtual environment activation and dependencies
2. **Type checking errors**: Run `mypy` for detailed error information
3. **Test failures**: Run specific test with `pytest -v` for detailed output
4. **Formatting issues**: Run `black .` to auto-format code
5. **Linting issues**: Run `ruff check --fix .` to auto-fix many issues

This AGENTS.md file provides comprehensive guidelines for AI agents working in this Mistral AI test project repository. Follow these guidelines to maintain code consistency, quality, and project standards.