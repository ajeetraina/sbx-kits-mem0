# sbx kits for mem0

This is a standalone [Docker Sandboxes](https://docs.docker.com/ai/sandboxes/) kit (`kind: mixin`) that adds the [Mem0](https://mem0.ai/) memory layer (`mem0ai`)
to any sandbox agent, pre-wired to a local [Docker Model Runner](https://docs.docker.com/ai/model-runner/) (DMR) for both the LLM and the embedder.


## Usage

DMR must be enabled on the host and the two models pulled before you start:

```console
$ docker model pull ai/gemma3              # LLM for memory extraction
$ docker model pull ai/mxbai-embed-large   # embedder (1024-dim)
```

Then layer the mixin onto an agent. From the published Docker Hub artifact
(recommended - no clone needed):

```console
$ sbx run --kit docker.io/ajeetraina777/sbx-mem0-kits:latest claude
```

Or straight from this repo over git:

```console
$ sbx run --kit "git+https://github.com/ajeetraina/sbx-kits-mem0.git" claude
```

Or from a local clone (the kit lives at the repo root):

```console
$ git clone https://github.com/ajeetraina/sbx-kits-mem0.git
$ sbx run --kit ./mem0-sbx-kits/ claude
```

Inside the sandbox, Mem0 is ready to use against DMR:

```python
import json
from mem0 import Memory

with open("/home/agent/.mem0/config.json") as f:
    m = Memory.from_config(json.load(f))

m.add([{"role": "user", "content": "I prefer dark roast coffee"}], user_id="alice")
print(m.search("what coffee do they like?", filters={"user_id": "alice"}))
```



