# Contributing to MistralAITests

Welcome to MistralAITests! We appreciate your interest in contributing to this project. This guide will help you get started with contributing to our codebase.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it to understand the expected behavior.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub. When reporting issues:

- Use a clear and descriptive title
- Provide detailed steps to reproduce the issue
- Include relevant code snippets or error messages
- Specify your environment (Python version, OS, etc.)

### Submitting Pull Requests

We welcome pull requests! Here's how to submit one:

1. **Fork the repository** and create your branch from `master`
2. **Install development dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Run tests** to ensure everything works:
   ```bash
   pytest
   ```

4. **Follow our coding standards**:
   - Use **Black** for code formatting: `black .`
   - Use **Ruff** for linting: `ruff check .`
   - Use **mypy** for type checking: `mypy .`
   - Write comprehensive tests for new features

5. **Commit your changes** with clear, descriptive messages following [Conventional Commits](https://www.conventionalcommits.org/)

6. **Push to your fork** and submit a pull request to our `master` branch

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ibitato/MistralAITests.git
   cd MistralAITests
   ```

2. Create and activate a virtual environment:
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

## Coding Standards

### Python Code

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for all functions and methods
- Write docstrings for all public functions and classes
- Keep line length under 88 characters
- Use double quotes for strings

### Testing

- Write tests for all new features and bug fixes
- Use pytest for testing
- Aim for 80%+ code coverage
- Test both happy paths and edge cases

### Documentation

- Update README.md if you add new features
- Keep docstrings up-to-date
- Document any breaking changes

## Review Process

All pull requests will be reviewed by maintainers. We may suggest changes or improvements before merging. Please be patient and responsive to feedback.

## Community

Join our [GitHub Discussions](https://github.com/ibitato/MistralAITests/discussions) to ask questions, share ideas, and connect with other contributors.

## License

By contributing to MistralAITests, you agree that your contributions will be licensed under the [MIT License](LICENSE).
