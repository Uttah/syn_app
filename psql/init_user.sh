#!/bin/bash

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER username WITH password 'password';
    GRANT ALL PRIVILEGES ON DATABASE postgres TO username;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public to USERNAME;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public to USERNAME;
    GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public to USERNAME;
EOSQL