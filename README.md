# sbx kits for mem0

This is a standalone [Docker Sandboxes](https://docs.docker.com/ai/sandboxes/) kit (`kind: mixin`) that adds the [Mem0](https://mem0.ai/) memory layer (`mem0ai`)
to any sandbox agent, pre-wired to a local [Docker Model Runner](https://docs.docker.com/ai/model-runner/) (DMR) for both the LLM and the embedder.

DMR is the zero-config default. It works with no cloud keys, but the embedder and LLM are both swappable. See [providers/](./providers/) for copy-paste config for OpenAI and Gemini.


## Prerequisites

### 1. Preparing the host 

Docker Model Runner must be enabled in Docker Desktop (Settings → AI / Beta features) and the two models pulled before you start:

```console
docker model pull ai/gemma3              # LLM for memory extraction
docker model pull ai/mxbai-embed-large   # embedder (1024-dim)
```

### 2. Launch the sandbox with the kit

Layer the mixin onto an agent. From the published Docker Hub artifact
(recommended - no clone needed):

```console
sbx run --kit docker.io/ajeetraina777/sbx-mem0-kits:latest claude
```

Or straight from this repo over git:

```console
sbx run --kit "git+https://github.com/ajeetraina/sbx-kits-mem0.git" claude
```

Or from a local clone (the kit lives at the repo root):

```console
git clone https://github.com/ajeetraina/sbx-kits-mem0.git
sbx run --kit ./mem0-sbx-kits/ claude
```

### 3. Confirm the kit installed correctly 

Once you're in the sandbox's Claude session, use ! shell escapes to check the wiring:
Inside the sandbox, Mem0 is ready to use against DMR:

```console
!python3 - <<'PY'
import os, json
for var in ("NO_PROXY", "no_proxy"):
    if var in os.environ:
          os.environ[var] = ",".join(e for e in os.environ[var].split(",") if e.strip() != "[::1]")

from mem0 import Memory

with open("/home/agent/.mem0/config.json") as f:
    m = Memory.from_config(json.load(f))

m.add([{"role": "user", "content": "I prefer dark roast coffee"}], user_id="alice")
print(m.search("what coffee do they like?", filters={"user_id": "alice"}))
PY
```

 ### 4. Check the sandbox can reach DMR on the host

 ```
!curl -s http://host.docker.internal:12434/engines/v1/models | head
```

Expect a JSON list including ai/gemma3 and ai/mxbai-embed-large. 

## Swapping the embedding / LLM provider

Mem0 is a semantic memory store, so an embedder is mandatory. There is no
"memory without embeddings" mode. DMR provides it locally by default, which
matters most for Claude agents: Anthropic
[ships no embeddings API](https://docs.anthropic.com/en/docs/build-with-claude/embeddings)
(it points to Voyage, which Mem0 doesn't support as a provider). OpenAI and Gemini
users can instead reuse one key for both the LLM and the embedder.

| Provider | Mem0 provider | Runs where | Credential | Example embed model | Dims |
|---|---|---|---|---|---|
| [DMR](./providers/dmr.md) (default) | `openai` (+ base_url) | local | none | `ai/mxbai-embed-large` | 1024 |
| [OpenAI](./providers/openai.md) | `openai` | cloud | `OPENAI_API_KEY` | `text-embedding-3-small` | 1536 |
| [Gemini](./providers/gemini.md) | `gemini` | cloud | `GOOGLE_API_KEY` | `models/gemini-embedding-001` | 768 |

Each page has the exact `config.json`, run command, and the dimension/network
notes. More detail: [providers/README.md](./providers/README.md).
