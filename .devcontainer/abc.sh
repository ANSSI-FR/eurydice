#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

groupadd --system --gid 1029 abc
useradd --uid 1029 --gid abc --no-log-init --create-home --shell /bin/bash abc
mkdir -p /home/abc/workdir
chown abc:abc /home/abc/workdir
