#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

make install-git-hooks
make install-dev
make create-dev-volumes

if [ -f "${__dir}/customize.sh" ]; then
    source "${__dir}/customize.sh" || true
fi
