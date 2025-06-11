#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

wget -qO- https://deb.nodesource.com/setup_20.x | bash -
apt-get install --no-install-recommends --no-install-suggests --yes --quiet nodejs
