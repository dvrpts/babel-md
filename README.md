# babel-md

Self-hosted REST API to convert PDF/DOCX/PPTX documents to Markdown/JSON.

Built with [Docling](https://github.com/DS4SD/docling) and [FastAPI](https://fastapi.tiangolo.com/).

## Quick Start

```bash
# Install dependencies
make init

# Run dev server
make dev

# Health check
curl http://localhost:8000/health
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | `""` | Gemini API key for image descriptions (optional) |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
| `GEMINI_BASE_URL` | `https://generativelanguage.googleapis.com/v1beta/openai` | Gemini OpenAI-compatible base URL |
| `HOST` | `0.0.0.0` | Server bind host |
| `PORT` | `8000` | Server bind port |
| `LOG_LEVEL` | `info` | Logging level |

## Usage

```bash
# PDF → Markdown
curl -X POST http://localhost:8000/v1/convert/file \
  -F "file=@sample.pdf" -G -d "output_format=markdown"

# DOCX → JSON
curl -X POST http://localhost:8000/v1/convert/file \
  -F "file=@sample.docx" -G -d "output_format=json"
```

## Docker

```bash
make docker-build
GEMINI_API_KEY=your-key make docker-run
```

## Development

```bash
make format   # Format code
make lint     # Run linter
make test     # Run tests
```

API docs available at http://localhost:8000/docs
