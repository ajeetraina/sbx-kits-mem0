#!/usr/bin/env bash
set -euo pipefail

namespace="${DOCKERHUB_NAMESPACE:-${DOCKER_NAMESPACE:-ajeetraina777}}"
tag="${TAG:-latest}"
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
image="docker.io/$namespace/sbx-mem0-kits"

# publish SPEC_DIR IMAGE_TAG README_FILE
# Stages a kit (spec.yaml + README + LICENSE), validates it, and pushes one tag.
publish() {
  local spec_dir="$1" image_tag="$2" readme="$3"
  local stage
  stage="$(mktemp -d /tmp/mem0-kits-push.XXXXXX)"
  mkdir -p "$stage/mem0"
  cp "$spec_dir/spec.yaml" "$stage/mem0/spec.yaml"
  cp "$readme" "$stage/mem0/README.md"
  cp "$repo_root/LICENSE" "$stage/mem0/LICENSE"
  sbx kit validate "$stage/mem0"
  sbx kit push "$stage/mem0" "$image:$image_tag"
  rm -rf "$stage"
  echo "Pushed $image:$image_tag"
}

# Default kit (DMR) at the repo root -> :$tag (default :latest).
publish "$repo_root" "$tag" "$repo_root/README.md"

# Per-provider kits under kits/ -> :<provider> (e.g. :dmr, :openai, :gemini).
# Each tag uses its provider doc as the image README. Those docs use repo-relative
# links (e.g. ../kits/openai); fine on GitHub, cosmetic-only on the Hub page.
for dir in "$repo_root"/kits/*/; do
  provider="$(basename "$dir")"
  readme="$repo_root/providers/$provider.md"
  [ -f "$readme" ] || readme="$repo_root/README.md"
  publish "$dir" "$provider" "$readme"
done
