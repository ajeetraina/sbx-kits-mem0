#!/usr/bin/env bash
#
# add-travel-example.sh
#
# Adds the travel-assistant example to the sbx-kits-mem0 kit using the files/
# tree. A path under files/home/ is copied to /home/agent/ inside every sandbox
# the kit builds, automatically, with no spec.yaml change required.
#
# Usage:
#   git clone https://github.com/ajeetraina/sbx-kits-mem0.git
#   cd sbx-kits-mem0
#   bash add-travel-example.sh
#
set -euo pipefail

if [[ ! -f spec.yaml ]]; then
  echo "error: spec.yaml not found. Run this from the root of your sbx-kits-mem0 clone." >&2
  exit 1
fi
if ! grep -Eq 'name:[[:space:]]*mem0' spec.yaml; then
  echo "warning: spec.yaml does not look like the mem0 kit. Continuing anyway." >&2
fi

mkdir -p files/home

cat > files/home/travel.py <<'PY'
#!/usr/bin/env python3
"""A tiny travel assistant that remembers the traveler across runs.

Ships with the sbx-kits-mem0 kit. Both the chat model and the Mem0 memory
layer talk to the local Docker Model Runner, so it runs with no cloud keys.

Usage (inside the sandbox):
    python3 ~/travel.py "I'm vegetarian, I like aisle seats. Book me to Lisbon."
    python3 ~/travel.py "Plan my return leg."     # a fresh process; it still knows you
"""
import os
import sys
import json

# sbx leaves an IPv6 "[::1]" entry in NO_PROXY that breaks the HTTP client's
# proxy-bypass matching, so calls to host.docker.internal get routed through the
# sandbox egress proxy and dropped. Strip it before any client is created.
for var in ("NO_PROXY", "no_proxy"):
    if var in os.environ:
        os.environ[var] = ",".join(e for e in os.environ[var].split(",") if e.strip() != "[::1]")

from openai import OpenAI
from mem0 import Memory

USER = "traveler_123"

# Chat model and memory both point at the local Docker Model Runner.
llm = OpenAI(base_url="http://host.docker.internal:12434/engines/v1", api_key="dmr")
with open("/home/agent/.mem0/config.json") as f:
    memory = Memory.from_config(json.load(f))


def reply(question):
    # Load everything we already know about this traveler, not just query matches.
    profile = [m["memory"] for m in memory.get_all(filters={"user_id": USER})["results"]]
    print("known so far:", profile or "(nothing yet)")

    prompt = (
        "You are a travel assistant.\n"
        f"What you already know about this traveler: {', '.join(profile)}\n\n"
        f"Traveler: {question}"
    )
    answer = llm.chat.completions.create(
        model="ai/gemma3",
        messages=[{"role": "user", "content": prompt}],
    ).choices[0].message.content

    memory.add(question, user_id=USER)  # remember it for next time
    return answer


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "Plan me a trip somewhere warm."
    print(reply(question))
PY

chmod 755 files/home/travel.py
echo "created: files/home/travel.py"

if command -v python3 >/dev/null 2>&1; then
  python3 -m py_compile files/home/travel.py && echo "ok: travel.py compiles"
  rm -rf files/home/__pycache__
fi

if [[ -d .git ]]; then
  git add files/home/travel.py
  echo
  echo "Staged. Review, then commit and push when ready:"
  echo "    git status"
  echo "    git commit -m 'Add travel-assistant example with NO_PROXY fix (files/home/travel.py)'"
  echo "    git push"
fi

echo
echo "Done. The kit now ships ~/travel.py into every sandbox it builds."
echo "No spec.yaml change needed: the files/ tree is copied in automatically."
