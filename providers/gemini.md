# Gemini 

Gemini *does* offer an embeddings API (similar to OpenAI).

| | |
|---|---|
| Mem0 provider | `gemini` |
| Runs where | Cloud (`generativelanguage.googleapis.com`) |
| Credential | `GOOGLE_API_KEY` |
| LLM model | `gemini-2.5-flash` |
| Embedder model | `models/gemini-embedding-001` |
| Vector dimensions | **768** |

## Network - edit `spec.yaml`

```yaml
network:
  allowedDomains:
    - generativelanguage.googleapis.com
    # ...existing entries
```

## Config - `/home/agent/.mem0/config.json`

```json
{
  "vector_store": {
    "provider": "qdrant",
    "config": {
      "collection_name": "mem0_gemini",
      "path": "/home/agent/.mem0/qdrant",
      "on_disk": true,
      "embedding_model_dims": 768
    }
  },
  "llm": {
    "provider": "gemini",
    "config": { "model": "gemini-2.5-flash" }
  },
  "embedder": {
    "provider": "gemini",
    "config": { "model": "models/gemini-embedding-001" }
  }
}
```

(The key is read from `GOOGLE_API_KEY`.)

## Run

```console
sbx run --kit docker.io/ajeetraina777/sbx-mem0-kits:latest \
  -e GOOGLE_API_KEY=... \
  claude
```


