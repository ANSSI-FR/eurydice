#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

matchown_volumes
/usr/local/share/devcontainer_entrypoint "$@"
