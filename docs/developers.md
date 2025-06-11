# 🚧 Development

## 🔨 Prerequisites

- `Linux environment`
- `make` (you can install it using `sudo apt-get install make`)
- [`docker>=25.0.2`](https://docs.docker.com/engine/install/)
  - watch mode has been introduced from [`docker compose version 2.22.0`](https://docs.docker.com/compose/releases/release-notes/#2220) and closest version is bundled into [`docker version 25.0.2`](https://docs.docker.com/engine/release-notes/25.0/#2502)
- access to docker images (see [🐳 Docker images](#-docker-images))
- `sudo` permissions to configure `sysctl` (optionally `ufw`)
- [`uv`](https://github.com/astral-sh/uv)

## 📁 Project structure

See [file-structure.md](file-structure.md).

## 📦 Versioning

See [versioning.md](versioning.md).

## 🐳 Docker images

See [docker-images.md](docker-images.md).

## 🏁 Usage

### ✨️ Installation

#### Step 0: Clone the project on your machine

```bash
git clone git@github.com:ANSSI-FR/eurydice.git
```

#### Step 1: Configure your firewall

In order to run Eurydice on your machine you will need to parametrize your firewall and your network configuration.
You will have to accept TCP connections on port **5000** (application side) and UDP on port **6000** (lidi side).

If you are using `ufw` to configure your firewall. You can run the following command:

```bash
make config-ufw
```

You'll be asked your sudo password. You should see the following:

```bash
sudo ufw allow 5000/tcp
sudo ufw allow 6000/udp
[sudo] password for <user>:
Rule added
Rule added
```

**Verify:** You can verify the configuration with:

```bash
sudo ufw status
```

You should see the following lines:

```bash
Status: active

To                         Action      From
--                         ------      ----
5000/tcp                   ALLOW       Anywhere
6000/udp                   ALLOW       Anywhere
```

**Note:** If you need to revert this configuration, you can run the following command:

```bash
make reset-ufw
```

You'll be asked your sudo password. You should see the following:

```bash
Rule deleted
Rule deleted
```

#### Step 2: Configure your network

For Eurydice's needs you will have to set up some network configuration for Lidi to be able to transfer files properly (see https://github.com/ANSSI-FR/lidi/blob/master/doc/tweaking.rst).

```bash
make config-sysctl
```

**Verify:** You can verify the configuration with:

```bash
sudo sysctl -n net.core.rmem_default -n net.core.rmem_default -n net.core.netdev_max_backlog -n  net.ipv4.udp_mem
```

You should see:

```bash
67108864
67108864
10000
12148128        16197504        24296256
```

**Note:** Your original sysctl config is backed up in the file sysctl_backup.conf. That is why you should only launch the this configuration once. If you need to revert the configuration, you can launch the following command:

```bash
make restore-sysctl
```

The configuration is not persistent so at next reboot it should come back to previous values.

#### Step 3: Copy environment file

Run the following command to copy the environment file:

```bash
cp .env.dev.example .env
```

You can adapt the variables inside the .env file corresponding to your needs (see [env.md](env.md) for more informations about env variables).

#### Step 4: Create the folders

Use the following command to create the directories required by Eurydice. The makefile recipe `create-dev-volumes` will try to import env variables from the `.env` file, and if they (`TRANSFERABLE_STORAGE_DIR`, `DB_DATA_DIR`, `DB_LOGS_DIR`, `FILEBEAT_LOGS_DIR`, `FILEBEAT_DATA_DIR`, `PYTHON_LOGS_DIR`) are not set, default values will be used.

```bash
make create-dev-volumes
```

### 🚀 Run the development environment

Make sure you have run the initialization once.
You have the choice to launch the dev stack with logs in elasticsearch or logs in console only:

```bash
# Development stack with basic console logging
make dev-up

# Development stack with advanced ElasticSearch logging using filebeat (accessible at `kibana.localhost`)
make dev-up-elk
```

The stack is launched with watch mode so that containers are automatically updated on changes on code (see [docker compose documentation](https://docs.docker.com/compose/how-tos/file-watch/)).

The following URLs are available in the development environment:

- <http://origin.localhost>: the origin user interface.
- <http://origin.localhost/api/docs/>: the origin API documentation.
- <http://origin.localhost/api/v1/>: the origin API.
- <http://origin.localhost/admin/>: the origin administration interface.
- <http://destination.localhost>: the destination user interface.
- <http://destination.localhost/api/docs/>: the destination API documentation.
- <http://destination.localhost/api/v1/>: the destination API.
- <http://destination.localhost/admin/>: the destination administration interface.
- <http://pgadmin.localhost/>: database management tool.
- <http://traefik.localhost/>: the traefik dashboard.
- <http://kibana.localhost/>: the kibana dashboard (if you launched dev-up-elk).

### 🛑 Stop the development environment

```bash
make dev-stop
```

### ⤵️ Install development dependencies

This command will locally install development dependencies for frontend and backend:

```bash
make install-dev
```

You will then be able to format, lint, test your code.

## ✨ Frontend

The developer documentation for the frontend of eurydice is available here: [`frontend/README.md`](../frontend/README.md).

## 🖥️ Backend

The developer documentation for the backend of eurydice is available here: [`backend/README.md`](../backend/README.md).
