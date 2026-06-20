#!/usr/bin/env python3
"""A tiny travel assistant that remembers the traveler across runs.

Ships with the sbx-kits-mem0 kit. Both the chat model and the Mem0 memory
layer talk to the local Docker Model Runner, so it runs with no cloud keys.

Usage (inside the sandbox):
    python3 travel.py "I'm vegetarian, I like aisle seats. Book me to Lisbon."
    python3 travel.py "Plan my return leg."     # a fresh process; it still knows you
"""
import sys
import json
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
