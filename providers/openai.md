# OpenAI (cloud)

If you already pay for OpenAI, you can power both halves from one key. The
LLM (fact extraction) and the embedder (semantic search) flow through the same
`openai` provider.

| | |
|---|---|
| Mem0 provider | `openai` |
| Runs where | Cloud (`api.openai.com`) |
| Credential | `OPENAI_API_KEY` |
| LLM model | `gpt-4o-mini` (or any chat model) |
| Embedder model | `text-embedding-3-small` (1536) or `text-embedding-3-large` (3072) |
| Vector dimensions | 1536 for `3-small` |

## Credential (store it as a secret, never on the command line)

`sbx run` has no `-e` flag, and you should never put a key in the command anyway.
Store it once with sbx's secret manager. `openai` is a built-in service, so the
proxy injects the key into outbound OpenAI requests and it never enters the
sandbox, shell history, or `ps`:

```bash
echo "$OPENAI_API_KEY" | sbx secret set -g openai   # -g = all sandboxes
# or run `sbx secret set -g openai` for an interactive prompt
```

The kit defaults `OPENAI_BASE_URL` to the local DMR endpoint, so the `config.json`
below pins `openai_base_url` to real OpenAI. A value set in the config takes
precedence over the env var.

## Network (edit `spec.yaml`)

Add the OpenAI host to `network.allowedDomains`, or the sandbox will block the
call:

```yaml
network:
  allowedDomains:
    - api.openai.com
    # ...existing entries
```

## Config (`/home/agent/.mem0/config.json`)

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
    "config": {
      "model": "gpt-4o-mini",
      "openai_base_url": "https://api.openai.com/v1"
    }
  },
  "embedder": {
    "provider": "openai",
    "config": {
      "model": "text-embedding-3-small",
      "openai_base_url": "https://api.openai.com/v1"
    }
  }
}
```

The API key is not in the config. It's supplied by the `sbx secret`
injection above, so nothing sensitive lives in `config.json`.

## Run

```console
# key already stored via `sbx secret set -g openai`
sbx run --kit docker.io/ajeetraina777/sbx-mem0-kits:latest claude
```

## Notes

Using `text-embedding-3-large` instead? That's 3072 dims, so change
`embedding_model_dims` to `3072` and start a fresh collection
(`rm -rf /home/agent/.mem0/qdrant` or a new `collection_name`).
