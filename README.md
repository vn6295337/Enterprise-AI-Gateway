---
title: Secure LLM Router API
emoji: 🔐
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# 🔐 Secure LLM Router API

A production-ready REST API with multi-provider LLM routing and comprehensive security features.

## Features

- **🔑 API Key Authentication**: X-API-Key header validation
- **⏱️ Rate Limiting**: 10 requests/minute per IP
- **✅ Input Validation**: Pydantic constraints on all parameters
- **🔄 Multi-Provider Fallback**: Gemini → Groq → OpenRouter cascade
- **📊 Health Monitoring**: Public health check endpoint
- **📝 Auto-Documentation**: OpenAPI/Swagger at `/docs`

## API Endpoints

### `GET /health`
Public health check endpoint (no authentication required)

```bash
curl https://YOUR-SPACE-URL/health
```

### `POST /query`
LLM query endpoint (requires API key authentication)

```bash
curl -X POST https://YOUR-SPACE-URL/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "prompt": "Explain quantum computing in one sentence",
    "max_tokens": 256,
    "temperature": 0.7
  }'
```

## Security Features

- **Authentication**: All `/query` requests must include valid `X-API-Key` header
- **Rate Limiting**: 10 requests per minute per IP address
- **Input Validation**:
  - `prompt`: 1-4000 characters
  - `max_tokens`: 1-2048
  - `temperature`: 0.0-2.0

## Configuration

This Space requires the following secrets to be configured:

1. **SERVICE_API_KEY**: API key for authenticating requests to this service
2. At least one LLM provider API key:
   - **GEMINI_API_KEY**: Google Gemini API key (primary)
   - **GROQ_API_KEY**: Groq API key (fallback)
   - **OPENROUTER_API_KEY**: OpenRouter API key (fallback)

## Tech Stack

- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **SlowAPI**: Rate limiting middleware
- **Pydantic**: Input validation
- **Multi-Provider LLM**: Gemini, Groq, OpenRouter

## Documentation

- Full API documentation available at `/docs` (Swagger UI)
- Redoc documentation at `/redoc`

## Repository

Source code: [github.com/vn6295337/poc-cloud-deploy](https://github.com/vn6295337/poc-cloud-deploy)
