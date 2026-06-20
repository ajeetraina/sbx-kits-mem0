#!/usr/bin/env python3
"""Local simulator for the composable-kits validation prototype.

Proves the core claim WITHOUT the sbx engine: the SAME provider kit and the
SAME channel kit feed BOTH agents, because the agent reconciles
/etc/sbx/agent-context.d at startup.

It mimics the sbx build/startup lifecycle in miniature:
  1. (build) copy each selected kit's agent-context.json into a temp context.d
  2. validate every fragment against the agent-context contract
  3. (startup) run each agent's reconcile.py against that context.d
  4. show what each agent rendered

Stdlib only. Run:
    python3 composable-kits/sim/simulate.py                 # full 2x2x2 matrix + worked example
    python3 composable-kits/sim/simulate.py --provider gemini --channel slack --agent atlas
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ROOT)  # composable-kits/

PROVIDERS = ["openai", "gemini"]
CHANNELS = ["telegram", "slack"]
AGENTS = ["nova", "atlas"]

REQUIRED_TOP = {"schemaVersion", "kind", "name", "config"}


def validate(frag, where):
    missing = REQUIRED_TOP - set(frag)
    if missing:
        raise ValueError(f"{where}: missing required fields {sorted(missing)}")
    if frag["schemaVersion"] != "1":
        raise ValueError(f"{where}: unsupported schemaVersion {frag['schemaVersion']!r}")
    if frag["kind"] not in ("provider", "channel"):
        raise ValueError(f"{where}: bad kind {frag['kind']!r}")
    role = frag.get("config", {}).get("role")
    if role not in ("llm-provider", "messaging-channel"):
        raise ValueError(f"{where}: bad config.role {role!r}")
    for s in frag.get("secrets", []):
        if "ref" not in s:
            raise ValueError(f"{where}: a secret entry has no 'ref'")
        if "value" in s:
            raise ValueError(f"{where}: secret carries a 'value' -- must be a ref only")


def fragment_path(kind, name):
    sub = "providers" if kind == "provider" else "channels"
    return os.path.join(BASE, sub, name, "agent-context.json")


def assemble_context(provider, channel):
    """The 'build' phase: every kit drops its fragment into context.d."""
    ctxd = tempfile.mkdtemp(prefix="ctxd-")
    for kind, name in (("provider", provider), ("channel", channel)):
        src = fragment_path(kind, name)
        with open(src) as f:
            frag = json.load(f)
        validate(frag, f"{kind}/{name}")
        shutil.copy(src, os.path.join(ctxd, f"{name}.json"))
    return ctxd


def run_agent(agent, ctxd):
    """The 'startup' phase: the agent reconciles context.d into its own config."""
    rec = os.path.join(BASE, "agents", agent, "reconcile.py")
    out_dir = tempfile.mkdtemp(prefix=f"{agent}-out-")
    env = dict(
        os.environ,
        AGENT_CONTEXT_DIR=ctxd,
        NOVA_CONFIG=os.path.join(out_dir, "nova.toml"),
        ATLAS_CONFIG=os.path.join(out_dir, "config.json"),
    )
    proc = subprocess.run([sys.executable, rec], env=env, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=PROVIDERS)
    ap.add_argument("--channel", choices=CHANNELS)
    ap.add_argument("--agent", choices=AGENTS)
    args = ap.parse_args()

    if args.provider and args.channel and args.agent:
        ctxd = assemble_context(args.provider, args.channel)
        rc, out, err = run_agent(args.agent, ctxd)
        print(f"== {args.agent}  <-  provider:{args.provider} + channel:{args.channel} ==\n")
        sys.stdout.write(out or err)
        sys.exit(rc)

    # Default: the full matrix, then one worked example.
    print("MATRIX  -- same provider + channel kits, both agents, every combo\n")
    header = f"{'provider':<10}{'channel':<10}" + "".join(f"{ag:<8}" for ag in AGENTS)
    print(header)
    print("-" * len(header))
    all_ok = True
    for p in PROVIDERS:
        for c in CHANNELS:
            ctxd = assemble_context(p, c)
            row = f"{p:<10}{c:<10}"
            for ag in AGENTS:
                rc, _, _ = run_agent(ag, ctxd)
                row += f"{'PASS' if rc == 0 else 'FAIL':<8}"
                all_ok = all_ok and rc == 0
            print(row)

    print("\nWORKED EXAMPLE  -- provider:openai + channel:telegram, fed to both agents\n")
    ctxd = assemble_context("openai", "telegram")
    for ag in AGENTS:
        fmt = "nova.toml (TOML)" if ag == "nova" else "config.json (JSON)"
        rc, out, err = run_agent(ag, ctxd)
        print(f"----- {ag} renders {fmt} -----")
        sys.stdout.write(out or err)
        print()

    print("Same two fragments -> two different native configs. No engine lifecycle change.")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
