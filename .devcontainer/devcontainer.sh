#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

UTILS_PACKAGES=""
apt-get update
apt-get --no-install-recommends --no-install-suggests --yes --quiet install \
    wget curl tree htop sudo apt-transport-https ca-certificates gnupg2 software-properties-common

wget -qO- https://download.docker.com/linux/debian/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"

apt-get update
apt-get --no-install-recommends --no-install-suggests --yes --quiet install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# add $USERNAME to `sudo` and `docker` group
USERNAME="${USERNAME:-abc}"
if id "${USERNAME}" &> /dev/null; then
    echo "${USERNAME} ALL=(root) NOPASSWD:ALL" > "/etc/sudoers.d/${USERNAME}"
    chmod 0440 "/etc/sudoers.d/${USERNAME}"
    usermod -a -G docker "${USERNAME}"
fi

# entrypoint
cat << "EOF" > /usr/local/share/devcontainer_entrypoint
#!/usr/bin/env bash
set -o errexit
groupmod --gid "$(stat -c '%g' /var/run/docker.sock)" docker
exec "$@"
EOF
chmod 0755 /usr/local/share/devcontainer_entrypoint

# cleanup
apt-get clean
apt-get --yes --quiet autoremove --purge
rm -rf /var/lib/apt/lists/* /tmp/*
