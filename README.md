# sbx kits for mem0

This is a standalone [Docker Sandboxes](https://docs.docker.com/ai/sandboxes/) kit (`kind: mixin`) that adds the [Mem0](https://mem0.ai/) memory layer (`mem0ai`)
to any sandbox agent, pre-wired to a local [Docker Model Runner](https://docs.docker.com/ai/model-runner/) (DMR) for both the LLM and the embedder.


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
import json
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

Expect a JSON list including ai/gemma3 and ai/mxbai-embed-large. If this hangs or errors, DMR isn't reachable — fix this before step 5 (it's the most common failure).



