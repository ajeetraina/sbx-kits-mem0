#!/usr/bin/env bash
set -euo pipefail


namespace="${DOCKERHUB_NAMESPACE:-${DOCKER_NAMESPACE:-ajeetraina777}}"
tag="${TAG:-latest}"
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
stage="$(mktemp -d /tmp/mem0-kits-push.XXXXXX)"

cleanup() {
  rm -rf "$stage"
}
trap cleanup EXIT


mkdir -p "$stage/mem0"
cp "$repo_root/spec.yaml" "$stage/mem0/spec.yaml"
cp "$repo_root/README.md" "$stage/mem0/README.md"
cp "$repo_root/LICENSE" "$stage/mem0/LICENSE"

sbx kit validate "$stage/mem0"
sbx kit push "$stage/mem0" "docker.io/$namespace/sbx-mem0-kits:$tag"

echo "Pushed docker.io/$namespace/sbx-mem0-kits:$tag"
