# OpenAI

OpenAI does offer an embeddings API (similar to Gemini).

| | |
|---|---|
| Mem0 provider | `openai` |
| Runs where | Cloud (`api.openai.com`) |
| Credential | `OPENAI_API_KEY` |
| LLM model | `gpt-4o-mini` (or any chat model) |
| Embedder model | `text-embedding-3-small` (1536) or `text-embedding-3-large` (3072) |
| Vector dimensions | **1536** for `3-small` |

## ⚠️ Override the DMR env first

The kit sets `OPENAI_BASE_URL` to the **DMR** endpoint and `OPENAI_API_KEY=dmr`.
Mem0's `openai` provider reads those, so for real OpenAI you must override both,
otherwise calls go to your local DMR instead of `api.openai.com`.

## Network — edit `spec.yaml`

Add the OpenAI host to `network.allowedDomains`, or the sandbox will block the
call:

```yaml
network:
  allowedDomains:
    - api.openai.com
    # ...existing entries
```

## Config — `/home/agent/.mem0/config.json`

```json
{
  "vector_store": {
    "provider": "qdrant",
    "config": {
      "collection_name": "mem0_openai",
      "path": "/home/agent/.mem0/qdrant",
      "on_disk": true,
      "embedding_model_dims": 1536
    }
  },
  "llm": {
    "provider": "openai",
    "config": { "model": "gpt-4o-mini" }
  },
  "embedder": {
    "provider": "openai",
    "config": { "model": "text-embedding-3-small" }
  }
}
```

(The API key is read from `OPENAI_API_KEY`; no need to inline it.)



