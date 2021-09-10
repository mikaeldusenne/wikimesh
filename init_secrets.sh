#!/bin/sh

function pwd(){
    < /dev/urandom tr -dc A-Za-z0-9 | head -c${1:-64};echo;
}

########
cd backend
echo "generating flask secret key..."
echo "FLASK_SECRET_KEY=$(pwd)" >> .env


########
cd ../mongo
echo "generating mongo user credentials..."

sed -ri "s/^.*(MONGO_INITDB_ROOT_PASSWORD).*$/export \1=$(pwd)/" .env
sed -ri "s/^.*(MONGO_INITDB_USER_PASSWORD).*$/export \1=$(pwd)/" .env

source ./.env
./create_setup_and_secrets.sh

