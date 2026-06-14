# Embedding and LLM providers for the Mem0 kit

Mem0 is a semantic memory store. The vector store is the memory. Every `add()`
embeds the extracted fact, and every `search()` embeds the query, so an embedder
is mandatory; there is no "memory without embeddings" mode. Mem0 also uses an LLM
internally to extract facts from a conversation and decide ADD / UPDATE /
skip-duplicate.

The kit ships wired to a local [Docker Model Runner](https://docs.docker.com/ai/model-runner/)
(DMR) for both halves, so it works with no cloud keys. But you can point either
half at OpenAI or Gemini instead. This folder has a focused page per provider with
copy-paste config.

Why DMR is the default (and why Claude users especially need it): Anthropic
[does not offer an embeddings model](https://docs.anthropic.com/en/docs/build-with-claude/embeddings).
Their docs point you to Voyage AI, and Mem0 has no Voyage embedder provider. So a
Claude-agent user has no cloud embedder in their existing credentials. DMR fills
that gap locally. OpenAI and Gemini users, by contrast, can reuse one key for both
the LLM and the embedder.

## Provider matrix

| Provider | Mem0 provider | Runs where | Credential | Example embed model | Dims |
|---|---|---|---|---|---|
| [DMR](./dmr.md) (default) | `openai` (+ base_url) | local | none | `ai/mxbai-embed-large` | 1024 |
| [OpenAI](./openai.md) | `openai` | cloud | `OPENAI_API_KEY` | `text-embedding-3-small` | 1536 |
| [Gemini](./gemini.md) | `gemini` | cloud | `GOOGLE_API_KEY` | `models/gemini-embedding-001` | 768 |

## Two gotchas that apply to every provider

1. Dimensions must match. Each embedder emits a fixed vector size (mxbai 1024,
   OpenAI 3-small 1536, Gemini 768). That number must appear in both the embedder
   config and `vector_store.config.embedding_model_dims`, and it must match the
   Qdrant collection. A mismatch causes Qdrant errors or garbage retrieval.
2. Changing dimensions needs a fresh collection. Qdrant won't let you mix vector
   sizes in one collection. When you switch providers, either change
   `collection_name` or delete the old store: `rm -rf /home/agent/.mem0/qdrant`.

## How to switch provider

The kit writes `/home/agent/.mem0/config.json` only if it's missing
(`onlyIfMissing: true`). To use a different provider, replace that file with the
one from the provider's page (or delete it and recreate it inside the sandbox),
then re-run the verify snippet. Cloud providers also need their API domain added to
`allowedDomains` in `spec.yaml`, and their API key stored with `sbx secret set`
(never passed on the command line; `sbx run` has no `-e` flag, and the proxy injects
the secret so it never enters the sandbox). Each page spells out exactly what.
