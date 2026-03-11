# API Reference

This section provides detailed documentation for the MistralAITests API and main components.

## MistralAIClient

The main client class for interacting with Mistral AI services.

### Constructor

```python
from src.mistral_client import MistralAIClient

client = MistralAIClient(api_key="your_api_key")
```

**Parameters:**
- `api_key` (str): Your Mistral AI API key
- `base_url` (str, optional): Base URL for API requests
- `timeout` (int, optional): Request timeout in seconds

### Chat Completion Methods

#### chat_completion

```python
def chat_completion(
    self,
    messages: list[dict[str, str]],
    temperature: float = 0.7,
    reasoning: bool = False
) -> str:
```

Get chat completion from Mistral AI.

**Parameters:**
- `messages`: List of chat messages (system, user, assistant)
- `temperature`: Temperature for completion (0.0 to 1.0)
- `reasoning`: Enable step-by-step reasoning

**Returns:** Completion text

#### chat_completion_stream

```python
def chat_completion_stream(
    self,
    messages: list[dict[str, str]],
    temperature: float = 0.7
) -> Iterator[str]:
```

Get streaming chat completion.

**Parameters:**
- `messages`: List of chat messages
- `temperature`: Temperature for completion

**Returns:** Iterator of response chunks

#### chat_completion_with_metrics

```python
def chat_completion_with_metrics(
    self,
    messages: list[dict[str, str]],
    temperature: float = 0.7
) -> dict:
```

Get chat completion with performance metrics.

**Parameters:**
- `messages`: List of chat messages
- `temperature`: Temperature for completion

**Returns:** Dictionary with content, duration, tokens, and metrics

### Tool Calling Methods

#### chat_completion_with_tools

```python
def chat_completion_with_tools(
    self,
    messages: list[dict[str, str]],
    tools: list[dict],
    temperature: float = 0.7
) -> dict:
```

Get chat completion with tool calling.

**Parameters:**
- `messages`: List of chat messages
- `tools`: List of available tools
- `temperature`: Temperature for completion

**Returns:** Dictionary with content and tool calls

#### execute_tool_calls

```python
def execute_tool_calls(
    self,
    tool_calls: list[dict]
) -> list[dict]:
```

Execute tool calls and return results.

**Parameters:**
- `tool_calls`: List of tool calls to execute

**Returns:** List of tool call results

### Vision Methods

#### vision_analysis

```python
def vision_analysis(
    self,
    image_url: str,
    prompt: str = "Describe this image in detail"
) -> str:
```

Analyze an image using Mistral AI vision capabilities.

**Parameters:**
- `image_url`: URL of the image to analyze
- `prompt`: Analysis prompt

**Returns:** Image description

#### vision_with_text

```python
def vision_with_text(
    self,
    image_url: str,
    text_prompt: str
) -> str:
```

Multimodal chat combining image and text.

**Parameters:**
- `image_url`: URL of the image
- `text_prompt`: Text prompt for the conversation

**Returns:** Combined response

### Batch Processing Methods

#### create_batch_job

```python
def create_batch_job(
    self,
    requests: list[dict],
    description: str = ""
) -> dict:
```

Create a batch processing job.

**Parameters:**
- `requests`: List of batch requests
- `description`: Job description

**Returns:** Batch job information

#### check_batch_status

```python
def check_batch_status(
    self,
    batch_id: str
) -> dict:
```

Check the status of a batch job.

**Parameters:**
- `batch_id`: Batch job ID

**Returns:** Batch job status

### Document Intelligence Methods

#### process_ocr

```python
def process_ocr(
    self,
    document_path: str,
    complex: bool = False
) -> dict:
```

Process OCR on a document.

**Parameters:**
- `document_path`: Path to the document
- `complex`: Enable complex OCR processing

**Returns:** OCR results

#### process_pdf

```python
def process_pdf(
    self,
    pdf_path: str,
    extract_tables: bool = True,
    extract_metadata: bool = True
) -> dict:
```

Process a PDF document.

**Parameters:**
- `pdf_path`: Path to the PDF file
- `extract_tables`: Extract tables from PDF
- `extract_metadata`: Extract metadata from PDF

**Returns:** PDF processing results

## DeterminismController

Controller for managing determinism levels in AI responses.

### Methods

#### set_determinism_level

```python
def set_determinism_level(
    self,
    level: int
) -> dict:
```

Set the determinism level.

**Parameters:**
- `level`: Determinism level (1-5)

**Returns:** Configuration parameters

#### get_determinism_params

```python
def get_determinism_params(
    self
) -> dict:
```

Get current determinism parameters.

**Returns:** Current configuration parameters

## DocumentManager

Manager for handling document uploads and retrieval.

### Methods

#### upload_document

```python
def upload_document(
    self,
    file_path: str
) -> dict:
```

Upload a document to Mistral AI.

**Parameters:**
- `file_path`: Path to the file to upload

**Returns:** Document information

#### list_documents

```python
def list_documents(
    self
) -> list:
```

List all uploaded documents.

**Returns:** List of documents

#### get_document_info

```python
def get_document_info(
    self,
    document_id: str
) -> dict:
```

Get information about a specific document.

**Parameters:**
- `document_id`: Document ID

**Returns:** Document information

#### delete_document

```python
def delete_document(
    self,
    document_id: str
) -> bool:
```

Delete a document.

**Parameters:**
- `document_id`: Document ID to delete

**Returns:** True if successful

## Error Handling

The library includes comprehensive error handling:

- `ValueError`: For invalid input parameters
- `RuntimeError`: For API communication errors
- `FileNotFoundError`: For missing files
- `PermissionError`: For access issues

All errors include descriptive messages to help with debugging.