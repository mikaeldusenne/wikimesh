# WikiMeSH

Detection of wikipedia pages in different languages for MeSH concepts

https://wikimesh.mikaeldusenne.com/

## Initialization

`./run.sh init` performs the project initialization that is actually supported by the helper script: it runs `./init_secrets.sh`, then builds and runs the `frontend.yml` + `init_frontend.yml` Compose stack to initialize frontend dependencies. It does not start the normal development or production stack.

For backend-only development, `./run.sh backend` starts the base services with `development.yml` but leaves the frontend Compose overlay out.

## Terminologies

To add another multilingual terminology, follow [Adding a terminology](docs/adding-terminology.md). It documents the CSV contract, import/fetch pipeline, validation steps and current matching limitations.

## Backend dependency updates

The backend runtime is pinned in `backend/Dockerfile` and CI. Direct dependencies live in `backend/requirements.txt`; deployments install `backend/requirements.lock`.

When updating dependencies, use a clean Python 3.14.6 environment, regenerate `requirements.lock` from `requirements.txt`, then run the CI before deployment. Mongo is intentionally excluded from routine image bumps because `./mongo/volume` contains persistent database files and requires a tested backup/upgrade path.

## MongoDB upgrades

Persistent MongoDB data is upgraded separately from routine container-image updates. See [the MongoDB upgrade runbook](docs/mongo-upgrade.md) and use `mongo/upgrade.sh`; never jump storage majors by changing the Compose image directly.
