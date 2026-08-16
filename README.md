# WikiMeSH

Detection of wikipedia pages in different languages for MeSH concepts

https://mikaeldusenne.com/wikimesh/

## Backend dependency updates

The backend runtime is pinned in `backend/Dockerfile` and CI. Direct dependencies live in `backend/requirements.txt`; deployments install `backend/requirements.lock`.

When updating dependencies, use a clean Python 3.14.6 environment, regenerate `requirements.lock` from `requirements.txt`, then run the CI before deployment. Mongo is intentionally excluded from routine image bumps because `./mongo/volume` contains persistent database files and requires a tested backup/upgrade path.
