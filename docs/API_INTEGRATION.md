# 🔌 Integration con Mistral AI API

## 🎯 Overview

Este documento detalla cómo el sistema se integra con la API de Mistral AI usando **Mistral AI Vibe CLI 2.2.1**, incluyendo endpoints, autenticación, manejo de errores y mejores prácticas.

**Desarrollado con:**
- **Mistral AI Vibe CLI**: 2.2.1
- **Modelo**: Devstral 2

**Créditos:**
Todos los ejemplos y desarrollos en este proyecto fueron creados utilizando las herramientas oficiales de Mistral AI, que proporcionan un entorno robusto y eficiente para trabajar con modelos de lenguaje.

## 📡 Autenticación

### Configuration de API Key

```python
# Desde variables de entorno
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("MISTRAL_AI_API_KEY")

# Validation
from utils import validate_api_key
if not validate_api_key(api_key):
    raise ValueError("Invalid API key")

# Uso en cliente
client = MistralAIClient(api_key=api_key)
```

### Formato de API Key

- **Longitud**: 32-64 caracteres
- **Formato**: Alfanumérico con guiones
- **Example**: `sk-1234567890abcdef1234567890abcdef`
- **Storage**: Variable de entorno (NUNCA en código)

## 📋 Endpoints de la API

### 1. Chat Completions

**Endpoint**: `POST https://api.mistral.ai/v1/chat/completions`

**Parameters:**

```json
{
  "model": "mistral-small-latest",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 1024,
  "top_p": 0.9,
  "stream": false,
  "random_seed": 42
}
```

**Response:**

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "mistral-small-latest",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 30,
    "total_tokens": 50
  }
}
```

**Implementation:**

```python
from mistral_client import MistralAIClient

client = MistralAIClient(api_key=api_key)
messages = [
    {"role": "user", "content": "What is the capital of France?"}
]

# Response completa
response = client.chat_completion(messages)
print(response)

# Streaming
for chunk in client.chat_completion_stream(messages):
    print(chunk, end="", flush=True)
```

### 2. File Upload

**Endpoint**: `POST https://api.mistral.ai/v1/files`

**Parameters:**

```json
{
  "file": {
    "file_name": "document.pdf",
    "content": "<binary_data>"
  },
  "purpose": "ocr"
}
```

**Response:**

```json
{
  "id": "file-123",
  "object": "file",
  "bytes": 102400,
  "created_at": 1234567890,
  "filename": "document.pdf",
  "purpose": "ocr",
  "sample_type": "ocr_input",
  "source": "upload",
  "mimetype": "application/pdf",
  "signature": "abc123"
}
```

**Implementation:**

```python
from document_manager import DocumentManager

doc_manager = DocumentManager(api_key)
file_info = doc_manager.upload_document("document.pdf", purpose="ocr")
print(f"File ID: {file_info.id}")
```

### 3. File List

**Endpoint**: `GET https://api.mistral.ai/v1/files`

**Parameters:**

None (returns list of all uploaded files)

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "file-123",
      "object": "file",
      "bytes": 102400,
      "created_at": 1234567890,
      "filename": "document.pdf",
      "purpose": "ocr"
    }
  ]
}
```

### 4. Batch Processing

**Endpoint**: `POST https://api.mistral.ai/v1/batch/jobs`

**Parameters:**

- **Input File**: JSONL file containing batch requests
- **Purpose**: `batch`

**Batch Request Format (JSONL):**

```json
{"custom_id": "request_01", "body": {"max_tokens": 60, "messages": [{"role": "user", "content": "Explain quantum computing"}]}}
{"custom_id": "request_02", "body": {"max_tokens": 60, "messages": [{"role": "user", "content": "Explain black holes"}]}}
```

**Requirements:**
- Minimum: 1 request per batch
- Maximum: 1,000 requests per batch
- File format: JSONL (JSON Lines)
- Each request must have unique `custom_id`

**Response:**

```json
{
  "id": "batch_job_123",
  "object": "batch",
  "status": "processing",
  "request_count": 50,
  "created_at": 1234567890
}
```

**Implementation:**

```python
from example_batch_processing import create_batch_file, submit_batch_job

# Create batch file with 50 requests
create_batch_file("batch_requests.jsonl", num_requests=50)

# Submit batch job
client = Mistral(api_key=api_key)
job_response = submit_batch_job(client, "batch_requests.jsonl")
print(f"Batch job submitted: {job_response.id}")
```

**Job Status Monitoring:**

```python
# Monitor job status
status = monitor_job_status(client, job_response.id)
print(f"Job status: {status}")

# Retrieve results when completed
if status == "completed":
    results = retrieve_results(client, job_response.id)
    for result in results:
        print(f"Request {result.custom_id}: {result.status}")
```

**Best Practices:**
- Use batches of 50-1,000 requests for optimal performance
- Include error handling for job monitoring
- Clean up batch files after processing
- Use unique custom_ids for tracking

- `page`: Número de página (default: 0)
- `page_size`: Tamaño de página (default: 100)
- `include_total`: Incluir total de documentos

**Response:**

```json
{
  "data": [
    {
      "id": "file-123",
      "object": "file",
      "bytes": 102400,
      "created_at": 1234567890,
      "filename": "document.pdf",
      "purpose": "ocr",
      "sample_type": "ocr_input",
      "source": "upload",
      "mimetype": "application/pdf",
      "signature": "abc123"
    }
  ],
  "object": "list",
  "total": 1
}
```

**Implementation:**

```python
documents = doc_manager.list_documents()
for doc in documents.data:
    print(f"{doc.filename} (ID: {doc.id})")
```

### 4. File Retrieve

**Endpoint**: `GET https://api.mistral.ai/v1/files/{file_id}`

**Response:**

```json
{
  "id": "file-123",
  "object": "file",
  "bytes": 102400,
  "created_at": 1234567890,
  "filename": "document.pdf",
  "purpose": "ocr",
  "sample_type": "ocr_input",
  "source": "upload",
  "mimetype": "application/pdf",
  "signature": "abc123",
  "deleted": false
}
```

**Implementation:**

```python
doc_info = doc_manager.get_document_info("file-123")
print(f"File: {doc_info.filename}, Size: {doc_info.bytes} bytes")
```

### 5. File Delete

**Endpoint**: `DELETE https://api.mistral.ai/v1/files/{file_id}`

**Response:**

```json
{
  "id": "file-123",
  "object": "file",
  "deleted": true
}
```

**Implementation:**

```python
success = doc_manager.delete_document("file-123")
if success:
    print("Document deleted successfully")
```

### 6. Get Signed URL

**Endpoint**: `GET https://api.mistral.ai/v1/files/{file_id}/url`

**Parameters:**

- `expiry`: Horas antes de que expire la URL (default: 24)

**Response:**

```json
{
  "url": "https://signed.url/document.pdf?expires=1234567890&signature=abc123"
}
```

**Implementation:**

```python
signed_url = doc_manager.get_signed_url("file-123", expiry_hours=12)
print(f"Signed URL: {signed_url}")
```

### 7. List Models

**Endpoint**: `GET https://api.mistral.ai/v1/models`

**Response:**

```json
{
  "data": [
    {
      "id": "mistral-small-latest",
      "object": "model",
      "created": 1234567890,
      "owned_by": "mistral"
    },
    {
      "id": "mistral-medium-latest",
      "object": "model",
      "created": 1234567890,
      "owned_by": "mistral"
    }
  ],
  "object": "list"
}
```

**Implementation:**

```python
models = client.list_models()
for model in models:
    print(model.id)
```

## 🔄 Document QnA con Files

### Formato de Messages

Para usar documentos subidos en chat completions:

```json
{
  "model": "mistral-small-latest",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "What is the main topic of this document?"},
        {"type": "file", "file_id": "file-123"}
      ]
    }
  ]
}
```

**Types de contenido soportados:**

1. **`text`**: Text simple
2. **`file_id`**: ID de archivo subido (deprecated, usar `file`)
3. **`file`**: ID de archivo subido (recomendado)
4. **`document_url`**: URL pública de documento
5. **`image_url`**: URL de imagen

### Implementation Completa

```python
# 1. Subir documento
doc_manager = DocumentManager(api_key)
file_info = doc_manager.upload_document("report.pdf", purpose="ocr")

# 2. Hacer pregunta sobre el documento
client = MistralAIClient(api_key)
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What is the main topic?"},
            {"type": "file", "file_id": file_info.id}
        ]
    }
]

response = client.chat_completion(messages)
print(f"Answer: {response}")

# 3. Limpiar
if doc_manager.delete_document(file_info.id):
    print("Document deleted")
```

## 📊 Métricas y Monitoreo

### Métricas de Uso

```python
metrics = client.chat_completion_with_metrics(messages)
print(f"Content: {metrics['content']}")
print(f"Duration: {metrics['duration']:.3f} seconds")
print(f"Tokens: {metrics['tokens']['total']}")
print(f"Tokens/second: {metrics['metrics']['tokens_per_second']:.1f}")
```

### Estructura de Métricas

```json
{
  "content": "Response text",
  "duration": 1.234,
  "tokens": {
    "prompt": 20,
    "completion": 30,
    "total": 50
  },
  "metrics": {
    "tokens_per_second": 40.65,
    "response_time_ms": 1234.56,
    "level": 3,
    "model": "mistral-small-latest"
  }
}
```

## ⚠️ Handling de Errors

### Errors Comunes y Soluciones

| Code de Error | Type | Causa | Solución |
|----------------|------|-------|----------|
| 401 | Unauthorized | API Key inválida | Verificar API Key en `.env` |
| 404 | Not Found | Resource no encontrado | Verificar IDs y endpoints |
| 429 | Too Many Requests | Límite de tasa excedido | Implementar retry con backoff |
| 500 | Internal Server Error | Error del servidor | Reintentar más tarde |
| 413 | Payload Too Large | File demasiado grande | Usar archivos < 512MB |
| 400 | Bad Request | Parameters inválidos | Validar entrada |

### Implementation de Handling de Errors

```python
try:
    response = client.chat_completion(messages)
    print(response)
except ValueError as e:
    print(f"Validation error: {e}")
    # Manejar error de validación
except RuntimeError as e:
    print(f"Runtime error: {e}")
    # Manejar error de ejecución
except Exception as e:
    print(f"Unexpected error: {e}")
    # Manejar error inesperado
    raise
```

### Retry con Backoff Exponencial

```python
import time
from mistralai import Mistral

def chat_with_retry(client, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.complete(messages=messages)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) * 0.1
            time.sleep(wait_time)
            continue
```

## 🛡️ Seguridad

### Buenas Prácticas

1. **API Key Management**:
   - Nunca en código fuente
   - Usar variables de entorno
   - Rotación periódica

2. **Validation de Input**:
   - Validar todos los parámetros
   - Limitar tamaño de archivos
   - Validar formatos

3. **Handling de Errors**:
   - No exponer información sensible
   - Logging seguro
   - Recuperación graceful

4. **Rate Limiting**:
   - Implementar retry con backoff
   - Monitorear uso de cuota
   - Alertas tempranas

### Example de Validation

```python
def validate_api_key(api_key):
    if not api_key:
        return False
    if not isinstance(api_key, str):
        return False
    if not api_key.startswith("sk-"):
        return False
    if len(api_key) < 32:
        return False
    return True
```

## 📈 Optimización

### Optimización de Costos

1. **Selección de Modelo**:
   - Usar `mistral-small-latest` para tareas simples
   - Usar `mistral-large-latest` solo cuando sea necesario

2. **Control de Tokens**:
   - Limitar `max_tokens`
   - Usar `temperature` adecuada
   - Optimizar prompts

3. **Cache de Responses**:
   - Cachear respuestas frecuentes
   - Usar TTL adecuado
   - Invalidar cache cuando sea necesario

### Optimización de Rendimiento

1. **Streaming**:
   - Usar streaming para respuestas largas
   - Procesamiento progresivo
   - Mejor experiencia de usuario

2. **Procesamiento por Lotes**:
   - Múltiples preguntas en un solo request
   - Procesamiento paralelo
   - Networkucir latencia

3. **Compresión**:
   - Comprimir documentos grandes
   - Usar formatos eficientes
   - Optimizar tamaño de payload

## 📚 Examples de Integration

### 1. Integration Básica

```python
from mistral_client import MistralAIClient

# Configuration
client = MistralAIClient(
    api_key="tu_api_key",
    model="mistral-small-latest",
    determinism_level=3
)

# Uso básico
messages = [{"role": "user", "content": "Hello!"}]
response = client.chat_completion(messages)
print(response)
```

### 2. Integration con Documents

```python
from document_manager import DocumentManager
from mistral_client import MistralAIClient

# Subir documento
doc_manager = DocumentManager(api_key)
file_info = doc_manager.upload_document("report.pdf", purpose="ocr")

# Preguntar sobre documento
client = MistralAIClient(api_key)
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What is the main topic?"},
            {"type": "file", "file_id": file_info.id}
        ]
    }
]
response = client.chat_completion(messages)
print(response)

# Limpiar
doc_manager.delete_document(file_info.id)
```

### 3. Integration con Streaming

```python
from mistral_client import MistralAIClient

client = MistralAIClient(api_key)
messages = [{"role": "user", "content": "Write a story about AI"}]

print("Story:")
for chunk in client.chat_completion_stream(messages):
    print(chunk, end="", flush=True)
print()
```

### 4. Integration con Métricas

```python
from mistral_client import MistralAIClient

client = MistralAIClient(api_key)
messages = [{"role": "user", "content": "Explain quantum computing"}]

metrics = client.chat_completion_with_metrics(messages)
print(f"Response: {metrics['content']}")
print(f"Tokens: {metrics['tokens']['total']}")
print(f"Time: {metrics['duration']:.3f}s")
```

## 🎯 Mejores Prácticas

### 1. Selección de Modelo

- **Empieza con `mistral-small-latest`**: Para la mayoría de los casos
- **Usa `mistral-large-latest`**: Solo para tareas complejas
- **Test diferentes modelos**: Compara resultados
- **Monitorea el uso**: Optimiza según necesidades

### 2. Control de Determinismo

- **Nivel 1-2**: Para respuestas precisas
- **Nivel 3**: Para uso general
- **Nivel 4-5**: Para creatividad
- **Ajusta dinámicamente**: Según el contexto

### 3. Handling de Files

- **Valida antes de subir**: Existencia, tamaño, tipo
- **Limpia después de usar**: Elimina archivos no necesarios
- **Usa URLs firmadas**: Para acceso temporal
- **Monitorea el almacenamiento**: Evita acumulación

### 4. Optimización de Prompts

- **Sé específico**: Prompts claros y concisos
- **Proporciona contexto**: Information relevante
- **Usa ejemplos**: Few-shot learning
- **Iteración**: Mejora basado en resultados

### 5. Handling de Errors

- **Valida entradas**: Antes de enviar a API
- **Maneja excepciones**: Graceful degradation
- **Logging**: Para depuración
- **Alertas**: Para errores críticos

## 🚀 Conclusión

La integración con Mistral AI API proporciona:

- ✅ **Fácil de usar**: SDK bien diseñado
- ✅ **Flexible**: Múltiples modelos y parámetros
- ✅ **Potente**: Capacidades avanzadas de IA
- ✅ **Escalable**: Soporte para crecimiento
- ✅ **Seguro**: Autenticación y validación robusta

Esta guía cubre todos los aspectos de la integración, desde autenticación hasta manejo avanzado de documentos y optimización de rendimiento.