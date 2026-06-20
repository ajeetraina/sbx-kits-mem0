import sys, json
from openai import OpenAI
from mem0 import Memory

llm = OpenAI(base_url="http://host.docker.internal:12434/engines/v1", api_key="dmr")
with open("/home/agent/.mem0/config.json") as f:
    memory = Memory.from_config(json.load(f))

USER = "traveler_123"

def reply(question):
    known = [h["memory"] for h in memory.search(question, filters={"user_id": USER})["results"]]
    print("recalled:", known or "(nothing yet)")
    prompt = ("You are a travel assistant.\n"
              f"What you already know about this traveler: {', '.join(known)}\n\n"
              f"Traveler: {question}")
    answer = llm.chat.completions.create(
        model="ai/gemma3",
        messages=[{"role": "user", "content": prompt}],
    ).choices[0].message.content
    memory.add(question, user_id=USER)
    return answer

print(reply(sys.argv[1]))
