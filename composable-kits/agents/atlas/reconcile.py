#!/usr/bin/env python3
"""Atlas reconciler.

Same job as Nova's reconciler, same agent-context.d input -- but Atlas emits a
completely different native format (JSON with a flattened env + secretRefs
block). The two agents share NO internal structure, yet both are driven by the
exact same provider and channel kits. That is the whole point of the contract.

Stdlib only.
"""
import glob
import json
import os
import sys

CONTEXT_DIR = os.environ.get("AGENT_CONTEXT_DIR", "/etc/sbx/agent-context.d")
OUT = os.environ.get("ATLAS_CONFIG", "/home/agent/atlas/config.json")


def main():
    frags = []
    for path in sorted(glob.glob(os.path.join(CONTEXT_DIR, "*.json"))):
        with open(path) as f:
            frags.append(json.load(f))

    providers = [f for f in frags if f.get("config", {}).get("role") == "llm-provider"]
    channels = [f for f in frags if f.get("config", {}).get("role") == "messaging-channel"]
    if len(providers) != 1:
        sys.exit(f"atlas: need exactly one llm-provider in {CONTEXT_DIR}, found {len(providers)}")

    pc = providers[0]["config"]
    config = {
        "llm": {
            "apiStyle": pc["apiStyle"],
            "endpoint": pc["baseUrl"],
            "model": pc["models"]["llm"],
            "embedModel": pc["models"]["embedder"],
            "keyRef": pc["auth"]["secretRef"],
        },
        "channels": [
            {
                "type": ch["config"]["transport"],
                "tokenRef": ch["config"]["auth"]["secretRef"],
            }
            for ch in channels
        ],
        "env": {k: v for fr in frags for k, v in fr.get("env", {}).items()},
        "secretRefs": sorted({s["ref"] for fr in frags for s in fr.get("secrets", [])}),
    }

    out = json.dumps(config, indent=2)
    out_dir = os.path.dirname(OUT)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(OUT, "w") as f:
        f.write(out + "\n")
    print(out)


if __name__ == "__main__":
    main()
