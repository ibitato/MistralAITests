# Getting Started with MistralAITests

Welcome to MistralAITests! This guide will help you set up the project and start testing Mistral AI services.

## Prerequisites

- Python 3.12 or higher
- Git
- Mistral AI API key

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ibitato/MistralAITests.git
cd MistralAITests
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file and add your Mistral AI API key:

```
MISTRAL_AI_API_KEY=your_api_key_here
```

## Running Tests

To verify everything is working correctly, run the test suite:

```bash
pytest
```

## Running Examples

The project includes several examples demonstrating Mistral AI capabilities:

### Basic Chat Completion

```bash
python src/example_determinism.py
```

### Tool Calling

```bash
python src/example_tool_calling.py
```

### Vision Capabilities

```bash
python src/example_vision.py
```

### Batch Processing

```bash
python src/example_batch_processing.py
```

## Code Quality Tools

### Formatting

```bash
black .
```

### Linting

```bash
ruff check .
```

### Type Checking

```bash
mypy .
```

## Next Steps

- Explore the [Features](features.md) section to learn about all capabilities
- Check out the [API Reference](api-reference.md) for detailed documentation
- Join our [GitHub Discussions](https://github.com/ibitato/MistralAITests/discussions) for community support