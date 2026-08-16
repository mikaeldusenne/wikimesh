#!/bin/bash

CMD="$1"
shift

docker_compose="docker compose"

set -xeu

case "$CMD" in
    ""|prod*)
        $docker_compose -f docker-compose.yml -f production.yml up --abort-on-container-exit $@
        ;;
    dev)
        $docker_compose -f docker-compose.yml  -f development.yml -f frontend.yml up --abort-on-container-exit $@
        ;;
    backend)
        $docker_compose  -f docker-compose.yml  -f development.yml up --abort-on-container-exit $@
        ;;
    init)
        echo "setting secrets..."
        ./init_secrets.sh
        echo "initializing frontend dependencies..."
        $docker_compose -f frontend.yml -f init_frontend.yml up --build --abort-on-container-exit $@
        ;;
    update-frontend)
        $docker_compose -f frontend.yml -f update_frontend.yml up --build --abort-on-container-exit $@
        ;;
	build*)
        $docker_compose -f frontend.yml -f build-front-end.yml up --abort-on-container-exit $@
        ;;
    lint*)
        docker exec -it wikimesh_vuecli_1 npm run lint
        ;;
    dump-db)
        docker exec -it wikimesh_mongo_docker sh -c "mongodump --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --db thedb --out /dumps/dump_$(date +'%Y-%m-%d_%H-%M-%S')"
        ;;
    restore-db)
        docker exec -i wikimesh_mongo_docker sh -c "mongorestore --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD /dumps/$1"
        ;;
    connect-db)
        . ./mongo/.env
        case "$1" in
            user)
                user=$MONGO_INITDB_USER_USERNAME
                pass=$MONGO_INITDB_USER_PASSWORD
            ;;
            root)
                user=$MONGO_INITDB_ROOT_USERNAME
                pass=$MONGO_INITDB_ROOT_PASSWORD
            ;;
        esac
        docker exec -it wikimesh_mongo_docker mongosh --username $user --password $pass
        ;;
    dev-venv-create)
        python -m venv venv && . ./venv/bin/activate \
            && pip install -r backend/requirements.txt \
            ;;
    init)
        $docker_compose -f docker-compose.yml -f frontend.yml build --no-cache && \
            ./run.sh update && \
            ./run.sh build --build && \
            ./run.sh 
        ;;
    stop)
        $docker_compose down
        ;;
    *)
        echo "unknown argument"
        exit 1
        ;;
esac

