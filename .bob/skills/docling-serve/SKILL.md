---
name: docling-serve
description: Extract structured data from unstructured documents (PDF, DOCX, images, etc.) using docling-serve API
---

Use the docling-serve API to extract content and structured data from unstructured documents.

## Workflow

When this skill is activated:

1. **Check for `.docling-env` file** in the project root
2. **If missing**, ask the user to provide:
   - Docling server URL (default: `http://localhost:5001`)
   - API key (optional, only if server has authentication enabled)
3. **Create `.docling-env`** with the provided configuration
4. **Proceed** with the document extraction task using the configured settings

## Configuration File

The `.docling-env` file should contain:

```bash
DOCLING_SERVER_URL=http://localhost:5001
DOCLING_API_KEY=your-api-key-here  # Optional, omit if no authentication
```

**Configuration variables:**
- `DOCLING_SERVER_URL`: The base URL of your docling-serve instance (required)
- `DOCLING_API_KEY`: API key for authentication (optional, only if enabled on server)

**Template:** A `.docling-env.example` file is provided in this skill directory as a reference.

## API Endpoints

The docling-serve API provides two main endpoints:

1. **`POST /v1/convert/source`** - For URLs or base64-encoded files
2. **`POST /v1/convert/file`** - For direct file uploads (multipart/form-data)

## Common Parameters

Key options to configure document processing:

- `from_formats`: Input formats (pdf, docx, pptx, html, image, xlsx, etc.)
- `to_formats`: Output formats (md, json, html, text, doctags)
- `do_ocr`: Enable OCR for bitmap content (default: true)
- `ocr_lang`: OCR languages (e.g., ["en", "fr", "de"])
- `pdf_backend`: PDF processing backend (dlparse_v2, docling_parse)
- `table_mode`: Table extraction mode (fast, accurate)
- `include_images`: Extract images from documents
- `do_table_structure`: Extract table structure
- `image_export_mode`: How to handle images (placeholder, embedded, referenced)

## Usage Examples

All examples use environment variables from `.docling-env`. Load them first:

```bash
source .docling-env
```

### Convert from URL

```bash
curl -X POST "${DOCLING_SERVER_URL}/v1/convert/source" \
  -H 'Content-Type: application/json' \
  -H "X-Api-Key: ${DOCLING_API_KEY}" \
  -d '{
    "sources": [{"kind": "http", "url": "https://arxiv.org/pdf/2408.09869"}],
    "options": {
      "to_formats": ["md", "json"],
      "do_ocr": true,
      "ocr_lang": ["en"]
    }
  }'
```

### Convert from File Upload

```bash
curl -X POST "${DOCLING_SERVER_URL}/v1/convert/file" \
  -H 'Content-Type: multipart/form-data' \
  -H "X-Api-Key: ${DOCLING_API_KEY}" \
  -F 'files=@document.pdf' \
  -F 'to_formats=md' \
  -F 'to_formats=json' \
  -F 'do_ocr=true' \
  -F 'ocr_lang=en'
```

### Convert Multiple Files

```bash
curl -X POST "${DOCLING_SERVER_URL}/v1/convert/file" \
  -H "X-Api-Key: ${DOCLING_API_KEY}" \
  -F 'files=@document1.pdf' \
  -F 'files=@document2.docx' \
  -F 'to_formats=md' \
  -F 'do_ocr=true'
```

### Convert with Base64-Encoded File

```bash
# Encode file to base64
B64_DATA=$(base64 -w 0 document.pdf)

# Create request body
cat <<EOF > /tmp/request.json
{
  "options": {
    "to_formats": ["md"]
  },
  "file_sources": [{
    "base64_string": "${B64_DATA}",
    "filename": "document.pdf"
  }]
}
EOF

# Send request
curl -X POST "${DOCLING_SERVER_URL}/v1/convert/source" \
  -H 'Content-Type: application/json' \
  -H "X-Api-Key: ${DOCLING_API_KEY}" \
  -d @/tmp/request.json
```

## Response Format

Single file response structure:

```json
{
  "document": {
    "md_content": "...",
    "json_content": {...},
    "html_content": "...",
    "text_content": "...",
    "doctags_content": "..."
  },
  "status": "success|partial_success|skipped|failure",
  "processing_time": 0.0,
  "errors": []
}
```

## Asynchronous API

For long-running conversions, use async endpoints:

### 1. Submit Async Task

```bash
# Submit conversion task
RESPONSE=$(curl -X POST "${DOCLING_SERVER_URL}/v1/convert/source/async" \
  -H 'Content-Type: application/json' \
  -H "X-Api-Key: ${DOCLING_API_KEY}" \
  -d '{
    "sources": [{"kind": "http", "url": "https://arxiv.org/pdf/2408.09869"}],
    "options": {"to_formats": ["md"]}
  }')

# Extract task_id
TASK_ID=$(echo $RESPONSE | jq -r '.task_id')
echo "Task ID: $TASK_ID"
```

### 2. Poll for Status

```bash
# Check task status
curl -X GET "${DOCLING_SERVER_URL}/v1/status/poll/${TASK_ID}" \
  -H "X-Api-Key: ${DOCLING_API_KEY}"
```

### 3. Fetch Result

```bash
# Get the result when task is complete
curl -X GET "${DOCLING_SERVER_URL}/v1/result/${TASK_ID}" \
  -H "X-Api-Key: ${DOCLING_API_KEY}"
```

### Complete Async Workflow

```bash
#!/bin/bash
source .docling-env

# Submit task
RESPONSE=$(curl -s -X POST "${DOCLING_SERVER_URL}/v1/convert/source/async" \
  -H 'Content-Type: application/json' \
  -H "X-Api-Key: ${DOCLING_API_KEY}" \
  -d '{"sources": [{"kind": "http", "url": "https://arxiv.org/pdf/2408.09869"}]}')

TASK_ID=$(echo $RESPONSE | jq -r '.task_id')
echo "Submitted task: $TASK_ID"

# Poll until complete
while true; do
  STATUS=$(curl -s -X GET "${DOCLING_SERVER_URL}/v1/status/poll/${TASK_ID}" \
    -H "X-Api-Key: ${DOCLING_API_KEY}")
  
  TASK_STATUS=$(echo $STATUS | jq -r '.task_status')
  echo "Status: $TASK_STATUS"
  
  if [[ "$TASK_STATUS" == "success" ]] || [[ "$TASK_STATUS" == "failure" ]]; then
    break
  fi
  
  sleep 2
done

# Fetch result
curl -X GET "${DOCLING_SERVER_URL}/v1/result/${TASK_ID}" \
  -H "X-Api-Key: ${DOCLING_API_KEY}"
```

## Authentication

Authentication is configured via the `.docling-env` file. If `DOCLING_API_KEY` is set, it will be automatically included in all requests as the `X-Api-Key` header.

## Best Practices

1. **Store credentials securely** - Keep `.docling-env` in `.gitignore` to avoid committing secrets
2. **Use async endpoints** for large documents or batch processing
3. **Set appropriate timeouts** via `document_timeout` option
4. **Enable OCR selectively** - only when needed for scanned documents
5. **Choose the right backend**: `dlparse_v2` for better accuracy, `pypdfium2` for speed
6. **Specify output formats** explicitly to avoid unnecessary processing
7. **Handle errors gracefully** - check `status` and `errors` fields in response
8. **Load environment once** - Cache the configuration at the start of your script

## Common Use Cases

- **Document conversion**: PDF → Markdown/HTML for display
- **Data extraction**: Extract tables, text, and images from reports
- **OCR processing**: Convert scanned documents to searchable text
- **Batch processing**: Use async API for multiple documents
- **Multi-format support**: Handle DOCX, PPTX, images, and more

## Reference

- API Documentation: `http://localhost:5001/docs`
- GitHub: https://github.com/docling-project/docling-serve
- Full docs: https://docling-project.github.io/docling-serve/