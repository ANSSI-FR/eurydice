#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PUID=${PUID:-1029}
PGID=${PGID:-1029}

# update permissions on volumes
if [ -n "${VOLUME_PATHS:-}" ]; then
    # split the volumes with ":"
    echo "${VOLUME_PATHS}" | tr ':' '\n' | while IFS= read -r VOLUME_PATH; do
        if [[ ! "$(stat -c %u "${VOLUME_PATH}")" == "${PUID}" ]]; then
            echo "Change in ownership detected, please wait while permissions are updated"
            matchown -R abc:abc "${VOLUME_PATH}"
        fi
    done
fi
