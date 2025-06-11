# Devcontainer

<https://containers.dev/implementors/json_reference/>

## Getting started

- run `make clean` to remove old `venv` and `node_modules`
- copy `.env.dev.example` to `.env`
- specify the `PUID` and `PGID` manually, or with this command : `printf "PUID=$(id -u)\nPGID=$(id -g)" >> .env`
- run `make create-dev-volumes`
- then open the devcontainer (`Ctrl + Shift + P` then `Dev Containers: ...`)
- please run the `migrations` tasks before running the services
