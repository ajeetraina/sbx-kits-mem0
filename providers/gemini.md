# Gemini — Google (cloud)

Power both halves from a Google AI Studio key. Gemini *does* offer an embeddings
API, so — like OpenAI — one key covers the LLM and the embedder.

| | |
|---|---|
| Mem0 provider | `gemini` |
| Runs where | Cloud (`generativelanguage.googleapis.com`) |
| Credential | `GOOGLE_API_KEY` |
| LLM model | `gemini-2.5-flash` |
| Embedder model | `models/gemini-embedding-001` |
| Vector dimensions | **768** |

## Network — edit `spec.yaml`

```yaml
network:
  allowedDomains:
    - generativelanguage.googleapis.com
    # ...existing entries
```

## Config — `/home/agent/.mem0/config.json`

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

## Gotchas

- **Model names move.** Google retires Gemini model ids over time. The pair
  validated here (June 2026) is `models/gemini-embedding-001` + `gemini-2.5-flash`;
  older ids like `text-embedding-004` and `gemini-1.5-flash` now return **404**.
  If you hit a 404, list what your key can actually use:
  ```python
  from google import genai
  for m in genai.Client(api_key="...").models.list():
      print(m.name, m.supported_actions)
  ```
- **Dimensions come from `output_dimensionality`.** `gemini-embedding-001`
  natively defaults to 3072 but supports Matryoshka truncation. Mem0 requests
  whatever `embedding_dims` is set to (defaulting to **768**), so the config
  above yields 768-dim vectors — matching `embedding_model_dims`. To use 1536 or
  3072, set `embedding_dims` in the embedder config **and** `embedding_model_dims`
  in `vector_store` to the same value, then start a fresh collection.
