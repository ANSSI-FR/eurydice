#!/usr/bin/env bash
# set -o xtrace

# Credits to Linuxserver.io and their `lsiown` script
# eg `docker run --rm -it ghcr.io/linuxserver/baseimage-ubuntu:jammy cat /usr/bin/lsiown`

# Usage:
# matchown -RcfvhHLP <user:group> <path> [path2 path3]

MAXDEPTH=("-maxdepth" "0")
OPTIONS=()
while getopts RcfvhHLP OPTION; do
    if [[ "${OPTION}" != "?" && "${OPTION}" != "R" ]]; then
        OPTIONS+=("-${OPTION}")
    fi
    if [[ "${OPTION}" = "R" ]]; then
        MAXDEPTH=()
    fi
done
shift "$((OPTIND - 1))"

USER_GROUP=$1
# split the user and the group
IFS=: read -r USER GROUP <<< "${USER_GROUP}"
if [[ -z "${GROUP}" ]]; then
    echo 'Expecting user:group format -- aborting'
    exit 0
fi

PATHS=("${@:2}")
/usr/bin/find "${PATHS[@]}" "${MAXDEPTH[@]}" \( ! -group "${GROUP}" -o ! -user "${USER}" \) -exec chown "${OPTIONS[@]}" "${USER}":"${GROUP}" {} + || echo "Permissions could not be set"
