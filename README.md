# mem0 sbx kits

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
$ sbx run --kit "git+https://github.com/ajeetraina/mem0-sbx-kits.git" claude
```

Or from a local clone (the kit lives at the repo root):

```console
$ git clone https://github.com/ajeetraina/mem0-sbx-kits.git
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

## Testing

After enabling DMR and pulling the two models (above):

```console
# 1. Validate the spec
$ sbx kit validate ./

# 2. Create a sandbox with the kit
$ sbx run --kit ./ --name mem0-probe claude .

# 3. Confirm the package installed and DMR is reachable from inside
$ sbx exec mem0-probe -- python3 -c "import mem0; print('mem0', mem0.__version__)"
$ sbx exec mem0-probe -- sh -c 'curl -s http://host.docker.internal:12434/engines/v1/models | head -c 400'

# 4. Functional round-trip: add -> search (exercises LLM + embedder + Qdrant)
$ sbx exec mem0-probe -- python3 - <<'PY'
import json
from mem0 import Memory
with open("/home/agent/.mem0/config.json") as f:
    m = Memory.from_config(json.load(f))
m.add([{"role": "user", "content": "I prefer dark roast coffee"}], user_id="alice")
print("RESULTS:", json.dumps(m.search("what coffee do they like?", filters={"user_id": "alice"}), indent=2)[:600])
PY

# 5. Clean up
$ sbx rm mem0-probe
```

**Pass criteria:** step 4 returns the coffee memory with no traceback that
proves the LLM (extraction), the embedder, and the on-disk Qdrant store all
worked against local DMR.

