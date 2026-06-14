# Hugging Face

Runs a `sentence-transformers` model **inside the Python process**, no separate
server, no API key, no cloud call at inference time. The model is downloaded once
from `huggingface.co`. Good for a fully offline embedder when you don't want to
run DMR or Ollama.

| | |
|---|---|
| Mem0 provider | `huggingface` |
| Runs where | In-process (CPU) |
| Credential | none |
| Embedder model | `sentence-transformers/all-MiniLM-L6-v2` (384) |
| Vector dimensions | **384** |
| Network | `huggingface.co` (model download only, first run) |

## Note on the LLM half

`huggingface` here covers the **embedder** only. Mem0 still needs an LLM for fact
extraction ~ keep that on DMR (`ai/gemma3`) or a cloud provider. The config below
pairs the HF embedder with the DMR LLM.

## Network ~ edit `spec.yaml`

Add the download host (only needed the first time the model is fetched):

```yaml
network:
  allowedDomains:
    - huggingface.co
    - cdn-lfs.huggingface.co
    # ...existing entries
```

## Config ~ `/home/agent/.mem0/config.json`

```json
{
  "vector_store": {
    "provider": "qdrant",
    "config": {
      "collection_name": "mem0_hf",
      "path": "/home/agent/.mem0/qdrant",
      "on_disk": true,
      "embedding_model_dims": 384
    }
  },
  "llm": {
    "provider": "openai",
    "config": {
      "model": "ai/gemma3",
      "openai_base_url": "http://host.docker.internal:12434/engines/v1",
      "api_key": "dmr"
    }
  },
  "embedder": {
    "provider": "huggingface",
    "config": { "model": "sentence-transformers/all-MiniLM-L6-v2" }
  }
}
```

## Run

```console
sbx run --kit docker.io/ajeetraina777/sbx-mem0-kits:latest claude
```


