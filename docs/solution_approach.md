# Solution Approach: LLM Router REST API

## Architecture

FastAPI service with two primary endpoints:

1. **GET /health** - Health check endpoint
   - Returns service status
   - Reports active LLM provider
   - Timestamp for uptime monitoring

2. **POST /query** - LLM query endpoint
   - Accepts JSON payload: `{prompt, max_tokens, temperature}`
   - Returns JSON response: `{response, provider, latency, status}`
   - Automatic provider fallback on failure

## Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Web Framework | FastAPI | Async support, automatic OpenAPI docs, type validation |
| ASGI Server | Uvicorn | Production-grade async server |
| LLM Providers | Gemini → Groq → OpenRouter | Multi-provider cascade (reuse from poc-rag) |
| Configuration | python-dotenv + config.py | Environment-based secrets management |
| Deployment | Hugging Face Spaces (Docker) | Free tier, 16GB RAM, proven success with poc-rag |
| Container | Python 3.11-slim | Lightweight, cross-platform compatibility |

## Data Flow

```
Client Request (POST /query)
        |
        v
+------------------+
| FastAPI Endpoint |  Validate input (Pydantic)
+------------------+
        |
        v
+------------------+
| LLM Cascade      |  Try Gemini → Groq → OpenRouter
| (src/config.py)  |  Return on first success
+------------------+
        |
        v
+------------------+
| Response Builder |  Format: {response, provider, latency, status}
+------------------+
        |
        v
JSON Response to Client
```

## Multi-Provider Fallback Logic

Reuse pattern from poc-rag:

1. **Primary**: Gemini API (15 RPM free tier)
   - Try first if `GEMINI_API_KEY` is set
   - On failure → fallback to Groq

2. **Fallback 1**: Groq API (30 RPM free tier, fastest)
   - Try if Gemini fails or key missing
   - On failure → fallback to OpenRouter

3. **Fallback 2**: OpenRouter (free models available)
   - Last resort provider
   - On failure → return error to client

## Deployment Strategy

**Hugging Face Spaces** (same as poc-rag):

- **Why**: Free tier with 16GB RAM, Docker support, proven successful
- **Entry point**: `app.py` at repository root (HF Spaces convention)
- **Port**: 7860 (HF Spaces default)
- **Environment**: Secrets configured via HF Spaces UI
- **Startup**: `start-app.sh` validates environment before launching uvicorn

## API Design

### Endpoint 1: Health Check

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "provider": "gemini",
  "model": "gemini-2.0-flash-exp",
  "timestamp": 1733558400.0
}
```

### Endpoint 2: LLM Query

**Request:**
```http
POST /query
Content-Type: application/json

{
  "prompt": "Explain quantum computing in one sentence",
  "max_tokens": 256,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "response": "Quantum computing uses quantum mechanics principles...",
  "provider": "gemini",
  "latency_ms": 1247,
  "status": "success"
}
```

**Error Response:**
```json
{
  "response": null,
  "provider": null,
  "latency_ms": 0,
  "status": "error",
  "error": "All LLM providers failed"
}
```

## Reuse from poc-rag

| Component | Reuse Strategy |
|-----------|----------------|
| Deployment platform | Hugging Face Spaces (Docker) - same approach |
| LLM provider pattern | Multi-provider cascade with graceful fallback |
| Configuration | Environment variables via python-dotenv |
| Entry points | app.py at root for HF Spaces compatibility |
| Startup script | start-app.sh with environment validation |
| Free-tier services | Same LLM providers (Gemini, Groq, OpenRouter) |

## Differences from poc-rag

| Aspect | poc-rag | poc-cloud-deploy |
|--------|---------|------------------|
| Interface | Streamlit UI | REST API (FastAPI) |
| Complexity | 5 components (RAG pipeline) | 2 endpoints (simple router) |
| Primary skill | RAG architecture | REST API design |
| Use case | Document Q&A | LLM service integration |
| Dependencies | sentence-transformers, Pinecone, Streamlit | FastAPI, uvicorn only |

## Performance Targets

- **Response time**: < 10s per query (LLM-dependent)
- **Cold start**: < 60s (Docker container initialization)
- **Uptime**: 99%+ through multi-provider redundancy
- **Cost**: $0/month (all free tiers)

## Error Handling

1. **Input validation**: Pydantic models reject malformed requests
2. **Provider failures**: Automatic cascade to next provider
3. **All providers fail**: Return error response with 500 status
4. **Missing API keys**: Startup validation prevents deployment
5. **Rate limits**: Return 429 status (no retry logic in PoC)

## Security Considerations

- **API Keys**: Environment variables only (never hardcoded)
- **CORS**: Not configured (PoC assumes trusted clients)
- **Rate limiting**: Not implemented (rely on provider limits)
- **Authentication**: Not implemented (PoC is public)

## Non-Goals (Intentionally Excluded)

- Vector database integration
- RAG pipeline
- Streaming responses
- User authentication
- Per-user rate limiting
- Persistent storage
- Logging infrastructure
- Horizontal scaling

These are excluded to keep the PoC focused on **REST API design** and **multi-provider orchestration**.
