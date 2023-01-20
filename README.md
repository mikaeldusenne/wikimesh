# WikiMeSH

Detection of wikipedia pages in different languages for MeSH concepts

https://mikaeldusenne.com/wikimesh/

## Run

./run.sh dev

## Load data

! You should be able to connect to the mongodb docker instance !
== Run the scripts from the app docker bash instance if the mongodb ports are not exposed to the host

### csv

python -m backend.src.mesh_parser --source <the_source_name> -i <the_name> backend/<filename>.csv

### Fetch data

python -m backend.src.db_feeder -i <the_name>
