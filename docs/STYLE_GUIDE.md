# 🎨 Mistral AI Examples Style Guide

## Overview

This style guide defines the standards for all example scripts in the Mistral AI Test Project. The goal is to provide a consistent, professional, and user-friendly experience across all examples.

## 1. File Structure

### Example Files
- Location: `src/example_*.py`
- Naming: `example_<feature>.py` (e.g., `example_batch_processing.py`)
- Purpose: Demonstrate real functionality with API

### Test Files
- Location: `tests/test_*.py`
- Naming: `test_<feature>.py` (e.g., `test_batch_processing.py`)
- Purpose: Validate functionality without API

### Data Files
- Location: `tests/test_data/`
- Purpose: Permanent datasets for examples
- Format: JSONL for batch files, PDF for documents

## 2. Code Structure

### Imports
```python
# Standard library
import os
import sys
import time
import logging
from typing import Optional

# Third-party
from colorama import Fore, Style, init
from dotenv import load_dotenv

# Local
from src.module import Class
```

### Main Function Structure
```python
def main() -> None:
    """Main function with standardized structure."""
    init(autoreset=True)
    start_time = time.time()
    
    # Setup logging
    logger.info("Starting example")
    
    # Print header
    print_header()
    
    # Step 1: Validation
    # Step 2: Initialization
    # Step 3: Execution
    # Step 4: Results
    # Step 5: Cleanup
    # Step 6: Summary
    
    logger.info(f"Completed in {time.time() - start_time:.2f}s")
```

## 3. Output Style

### Header Format
```python
def print_header():
    print("\n" + "=" * 60)
    print("🚀 EXAMPLE NAME")
    print("=" * 60)
    print("Description of what this example demonstrates")
    print("=" * 60 + "\n")
```

### Step Format
```python
print("\n1️⃣  Step description...")
# Execution
print_success("✅ Step completed")
print(f"   📊 Metrics: value")
```

### Message Types

#### Success
```python
def print_success(message: str):
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
```

#### Error
```python
def print_error(message: str, details: str = ""):
    print(f"\n{Fore.RED}❌ Error: {message}{Style.RESET_ALL}")
    if details:
        print(f"   {details}")
```

#### Warning
```python
def print_warning(message: str):
    print(f"\n{Fore.YELLOW}⚠️  Warning: {message}{Style.RESET_ALL}")
```

### Summary Format
```python
print("\n" + "=" * 60)
print("✅ EXAMPLE COMPLETED")
print("=" * 60)

print("\n📊 Results:")
print("   • Metric 1: Value")
print("   • Metric 2: Value")
print(f"   • Time: {elapsed_time:.2f} seconds")

print("\n📚 Resources:")
print("   • Documentation: docs/API_INTEGRATION.md")
print("   • All Examples: python main_examples.py")
print("   • Mistral AI: https://mistral.ai")

print("\n💡 Tips:")
print("   • Tip 1")
print("   • Tip 2")
print("   • Tip 3")
```

## 4. Logging

### Configuration
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('<example_name>.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Suppress mistralai SDK logs
logging.getLogger("mistralai").setLevel(logging.WARNING)
```

### Log Levels
- **DEBUG**: Detailed technical information (development only)
- **INFO**: Normal operation messages (default)
- **WARNING**: Potential issues (user visible)
- **ERROR**: Critical failures (user visible)

### Log Messages
```python
logger.debug("Detailed technical info")  # Development only
logger.info("Operation started")        # Normal operation
logger.warning("Potential issue detected")  # User visible
logger.error("Critical failure", exc_info=True)  # User visible with traceback
```

## 5. Error Handling

### Validation
```python
def validate_api_key(api_key: str) -> bool:
    """Validate API key format."""
    if not api_key:
        return False
    if not isinstance(api_key, str):
        return False
    if len(api_key) < 32:
        return False
    return True
```

### Exception Handling
```python
try:
    # Operation
    result = risky_operation()
except ValidationError as e:
    print_error("Invalid input", str(e))
    logger.error(f"Validation error: {str(e)}")
    return
except ApiConnectionError as e:
    print_error("API connection failed", str(e))
    logger.error(f"API error: {str(e)}")
    return
except Exception as e:
    print_error("Unexpected error", str(e))
    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    return
finally:
    cleanup_resources()
```

### Custom Exceptions
```python
class BatchProcessingError(Exception):
    """Custom exception for batch processing errors."""
    pass

class ApiConnectionError(Exception):
    """Custom exception for API connection errors."""
    pass

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass
```

## 6. Cleanup

### File Cleanup
```python
def cleanup_batch_file(file_path: str) -> bool:
    """Safely clean up a batch file."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Removed file: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return False
```

### Resource Management
```python
# Always clean up in finally block
try:
    # Use resources
    process_data()
finally:
    cleanup_resources()
```

## 7. Documentation

### Docstrings
```python
def function_name(param: type) -> return_type:
    """Brief description.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: Description of when raised
        
    Example:
        >>> function_name(value)
        result
    """
    # Implementation
    return value
```

### Comments
```python
# Good: Explains why, not what
# Bad: result = a + b  # Add a and b

# Calculate total to ensure we don't exceed API limits
total_requests = len(batch_1) + len(batch_2)
```

## 8. Testing

### Test Structure
```python
class TestFeature:
    """Test cases for feature."""
    
    def test_functionality(self):
        """Test that functionality works."""
        result = function()
        assert result == expected
    
    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ExpectedError):
            function(invalid_input)
```

### Test Data
- Location: `tests/test_data/`
- Format: Permanent datasets with `.jsonl` extension
- Usage: Read-only in tests

## 9. Best Practices

### Code Quality
- Follow PEP 8 style guide
- Use type hints
- Keep functions small (< 50 lines)
- Single responsibility principle
- DRY (Don't Repeat Yourself)

### User Experience
- Clear, concise messages
- Actionable error messages
- Progress indicators
- Success confirmation
- Next steps guidance

### Performance
- Measure execution time
- Log performance metrics
- Optimize I/O operations
- Use efficient data structures

### Security
- Never log API keys
- Validate all inputs
- Use environment variables for secrets
- Clean up temporary files

## 10. Example Template

```python
"""
Example script demonstrating [Feature].

Shows how to [brief description].
"""

import os
import time
import logging
from typing import Optional

from colorama import Fore, Style, init
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('<example>.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Suppress mistralai SDK logs
logging.getLogger("mistralai").setLevel(logging.WARNING)


def print_header():
    """Print standardized header."""
    print("\n" + "=" * 60)
    print("🚀 EXAMPLE NAME")
    print("=" * 60)
    print("Description")
    print("=" * 60 + "\n")


def print_error(message: str, details: str = ""):
    """Print error message."""
    print(f"\n{Fore.RED}❌ Error: {message}{Style.RESET_ALL}")
    if details:
        print(f"   {details}")


def print_success(message: str):
    """Print success message."""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")


def main() -> None:
    """Main function."""
    init(autoreset=True)
    start_time = time.time()
    
    logger.info("Starting example")
    print_header()
    
    # Steps with error handling
    # ...
    
    # Summary
    elapsed = time.time() - start_time
    print_summary(elapsed)
    logger.info(f"Completed in {elapsed:.2f}s")


def print_summary(elapsed: float):
    """Print completion summary."""
    print("\n" + "=" * 60)
    print("✅ COMPLETED")
    print("=" * 60)
    print(f"\nTime: {elapsed:.2f} seconds")
    print("\nNext: python main_examples.py")


if __name__ == "__main__":
    main()
```

## 11. Compliance Checklist

- [ ] Follows file structure standards
- [ ] Uses standardized output format
- [ ] Implements proper error handling
- [ ] Includes comprehensive logging
- [ ] Has complete docstrings
- [ ] Cleans up resources
- [ ] Validates inputs
- [ ] Handles edge cases
- [ ] Provides clear user feedback
- [ ] Follows PEP 8 style
- [ ] Has type hints
- [ ] Includes tests
- [ ] Documents exceptions

## 12. Version Information

**Mistral AI Vibe CLI**: 2.2.1
**Model**: Devstral 2
**Python Version**: 3.10+
**Last Updated**: 2024
**Style Guide Version**: 1.0

## 13. Changelog

### 1.0 (Current)
- Initial style guide
- Applied to all examples
- Standardized error handling
- Improved logging
- Consistent output format

### Future
- Add more examples
- Enhance test coverage
- Improve documentation
- Add performance benchmarks

---

**Note**: This style guide is a living document. Updates will be made as the project evolves.
