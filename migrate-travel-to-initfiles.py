#!/usr/bin/env python3
"""
migrate-travel-to-initfiles.py

Moves the travel-assistant demo from files/home/travel.py into the kit's
`commands.initFiles` so it ships inside the published Hub image (not just the
git-source install). Run from the root of your sbx-kits-mem0 clone:

    python3 migrate-travel-to-initfiles.py

What it does:
  1. Reads the current files/home/travel.py (your verified script).
  2. Adds it as an initFiles entry (mode 0755) to every DMR spec.yaml:
       - ./spec.yaml          (builds the :latest tag)
       - ./kits/dmr/spec.yaml (builds the :dmr tag, if present)
     It SKIPS kits/openai and kits/gemini on purpose: travel.py points its
     chat client at the local Docker Model Runner, so it's a DMR-only demo.
  3. Removes files/home/travel.py (git rm) so there's one source of truth.
  4. Runs `sbx kit validate` on each patched kit dir if sbx is on PATH.

It's idempotent: a spec that already has the travel.py entry is left alone.
Review `git diff` and re-run `sh scripts/push-kits.sh` afterward.
"""
import os
import sys
import subprocess

TRAVEL_SRC = "files/home/travel.py"
TARGET_PATH = "/home/agent/travel.py"
SPEC_CANDIDATES = ["spec.yaml", "kits/dmr/spec.yaml"]


def die(msg):
    print(f"\nERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def ensure_ruamel():
    try:
        import ruamel.yaml  # noqa: F401
        return
    except ImportError:
        print("Installing ruamel.yaml (round-trip YAML editor)...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet",
             "--break-system-packages", "ruamel.yaml"],
            check=False,
        )
        try:
            import ruamel.yaml  # noqa: F401
        except ImportError:
            die("could not install ruamel.yaml. Run: pip install ruamel.yaml")


def load_travel_source():
    if not os.path.isfile(TRAVEL_SRC):
        die(f"{TRAVEL_SRC} not found. Run this from the repo root, and make "
            f"sure the file still exists (git checkout it if you removed it).")
    with open(TRAVEL_SRC, "r") as f:
        src = f.read()
    # Literal blocks read cleanest with exactly one trailing newline.
    return src.rstrip("\n") + "\n"


def patch_spec(path, travel_src):
    from ruamel.yaml import YAML
    from ruamel.yaml.scalarstring import LiteralScalarString, DoubleQuotedScalarString
    from ruamel.yaml.comments import CommentedMap

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096
    yaml.indent(mapping=2, sequence=4, offset=2)

    with open(path, "r") as f:
        data = yaml.load(f)

    if "commands" not in data or data["commands"] is None:
        data["commands"] = CommentedMap()
    commands = data["commands"]
    if "initFiles" not in commands or commands["initFiles"] is None:
        commands["initFiles"] = []
    init_files = commands["initFiles"]

    # Idempotency: bail if travel.py is already declared.
    for entry in init_files:
        if isinstance(entry, dict) and entry.get("path") == TARGET_PATH:
            print(f"  - {path}: already has {TARGET_PATH}, skipping")
            return False

    entry = CommentedMap()
    entry["path"] = TARGET_PATH
    entry["mode"] = DoubleQuotedScalarString("0755")
    entry["onlyIfMissing"] = True
    entry["description"] = "Travel-assistant demo (runs against local Docker Model Runner)"
    entry["content"] = LiteralScalarString(travel_src)
    init_files.append(entry)

    with open(path, "w") as f:
        yaml.dump(data, f)
    print(f"  - {path}: added {TARGET_PATH}")
    return True


def validate(kit_dir):
    if subprocess.run(["which", "sbx"], capture_output=True).returncode != 0:
        print(f"  - sbx not on PATH, skipping validate for {kit_dir}")
        return
    res = subprocess.run(["sbx", "kit", "validate", kit_dir],
                         capture_output=True, text=True)
    status = "OK" if res.returncode == 0 else "FAILED"
    print(f"  - validate {kit_dir}: {status}")
    if res.returncode != 0:
        print(res.stdout.strip())
        print(res.stderr.strip())


def main():
    if not os.path.isfile("spec.yaml"):
        die("spec.yaml not found. Run this from the root of your sbx-kits-mem0 clone.")

    ensure_ruamel()
    travel_src = load_travel_source()

    print("Patching DMR spec files:")
    patched_any = False
    for spec in SPEC_CANDIDATES:
        if not os.path.isfile(spec):
            print(f"  - {spec}: not present, skipping")
            continue
        if patch_spec(spec, travel_src):
            patched_any = True

    print("\nValidating kits:")
    validate(".")
    if os.path.isfile("kits/dmr/spec.yaml"):
        validate("kits/dmr")

    # Single source of truth: drop the now-redundant static copy.
    if os.path.isfile(TRAVEL_SRC):
        print("\nRemoving the redundant static copy:")
        rm = subprocess.run(["git", "rm", TRAVEL_SRC], capture_output=True, text=True)
        if rm.returncode == 0:
            print(f"  - git rm {TRAVEL_SRC}")
        else:
            os.remove(TRAVEL_SRC)
            print(f"  - removed {TRAVEL_SRC} (was untracked)")

    print("\nDone.")
    if patched_any:
        print("Next steps:")
        print("  git diff                       # review the spec.yaml change")
        print("  git add -A && git commit -m 'Ship travel.py via initFiles'")
        print("  git push")
        print("  sh scripts/push-kits.sh        # re-publish the Hub tags")
        print("  sbx rm shell-sbx-kits-mem0")
        print("  sbx run --kit docker.io/ajeetraina777/sbx-mem0-kits:latest shell")
        print("  # inside: ls ~/travel.py  &&  python3 ~/travel.py \"...\"")
    else:
        print("No specs needed changes (already migrated).")


if __name__ == "__main__":
    main()
