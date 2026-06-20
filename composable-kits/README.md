# composable-kits — validation prototype

A runnable proof that **provider** and **channel** kits can be reused across
**different agents** *without* changing the sbx engine — by faking "the agent
gets the last word" with build-time fragments + a startup reconcile.

This is the Path-1 spike. It does not need the sbx runtime; everything here runs
locally with stdlib Python.

## The problem it answers

The agent kit needs to configure itself **knowing what the provider/channel kits
did** — but kits apply in one pass and the agent has no "second turn" at the end.
The proper fix is an engine **lifecycle change** (a stage that hands control back
to the agent after all kits apply). That's real engine work.

## The workaround being validated

1. **Build time** — every provider/channel kit drops a small JSON *fragment*
   into `/etc/sbx/agent-context.d/<name>.json` describing what it set up
   (`initFiles`, declarative). This is the "sticky note."
2. **Startup time** — the agent kit's `startup` command reads *all* the
   fragments and renders its own native config. Startup always runs after every
   kit's build-time `initFiles`, so the agent effectively goes last — **no engine
   change required.**

The fragment format (`agent-context.schema.json`) **is the contract** that makes
one provider/channel kit work for any agent.

> Why fragments are written at build time, not in the kit's own startup: if both
> the kits and the agent wrote during `startup`, we'd need "agent startup runs
> last" — the exact ordering guarantee we're trying to avoid. Build-time
> `initFiles` always precede any `startup`, so the ordering is free.

## What's here

```
agent-context.schema.json     the contract (JSON Schema)
providers/openai|gemini/      provider kits: spec.yaml + agent-context.json fragment
channels/telegram|slack/      channel kits: spec.yaml + agent-context.json fragment
agents/nova|atlas/            agent kits: spec.yaml + reconcile.py (renders native config)
sim/simulate.py               local simulator (stdlib only)
```

`nova` renders **TOML**, `atlas` renders **JSON** — two agents that share nothing
internally, both driven by the same kits. That's the reuse claim, made concrete.

## Run it

```sh
python3 composable-kits/sim/simulate.py
```

Output: a 2×2×2 matrix (openai/gemini × telegram/slack × nova/atlas, all PASS),
then a worked example showing the *same* two fragments rendered into each agent's
native config. Pick one combo with
`--provider gemini --channel slack --agent atlas`.

## How it maps to the gaps from the meeting

- **"oauth/secrets missing in mixins"** → provider/channel kits declare a
  first-class `secrets:` block (and the fragment carries `auth.secretRef`).
  Secrets are **refs, never values** — the sbx proxy / a 1Password ref resolves
  them at runtime. Slack shows two-token auth; Telegram shows one.
- **"docker image missing in mixin"** → agent kits declare a base `image:`.
  Kits layer on top of it.
- **"agent configures itself in presence of provider config"** → the
  `startup` reconcile, reading `agent-context.d`. The agent owns conflict
  resolution (e.g. nova/atlas require exactly one `llm-provider` and error
  otherwise).

## Honest limitation (worth raising with the engine team)

This handles **config-time** reconciliation cleanly. It does **not** cleanly
handle **build-time** decisions — e.g. an agent needing to `pip install` a
provider-specific SDK based on which provider is present, since installs happen
during the merge, before the agent can look.

Mitigation, and the line to hold: keep build-time concerns **inside each kit**
(the existing Gemini mem0 kit already installs `google-genai` itself). Only
**config crosses the kit boundary**, and config defers cleanly to startup. That's
enough to validate the "2 agents × reusable provider/channel kits" story before
asking the engine team for the real lifecycle change — which remains the
production-grade design.
