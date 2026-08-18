#!/bin/bash

set -eo pipefail

DATE=$(date +%Y%m%d_%H%M%S)
FILE="$TARGET_FOLDER/backup-$DATE.gz"

echo "Job started: $(date)"

mkdir -p "$TARGET_FOLDER"
mongodump \
    --host="wikimesh_mongo_docker" \
    --archive="$FILE" \
    --gzip \
    --username "$MONGO_INITDB_ROOT_USERNAME" \
    --password "$MONGO_INITDB_ROOT_PASSWORD" \
    --db "$MONGO_INITDB_DATABASE"

echo "Mongo dump saved to $FILE"
echo "Job finished: $(date)"
