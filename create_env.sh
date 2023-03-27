#!/bin/bash

#
# postgres envs
#
cat <<EOF > .env
  # postgres envs
  POSTGRES_DB=postgres
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=postgres
EOF

#
# fastapi envs
#
SECRET_KEY=`openssl rand -hex 32`

cat <<EOF > ./backend/.env
  # authentication
  SECRET_KEY = "${SECRET_KEY}"
  ALGORITHM = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES = 30
  REFRESH_TOKEN_EXPIRE_MINUTES = 10080

  # fastapi db connection
  # db name defines on 'compose.yml' services
  DB_URL="postgresql://postgres:postgres@postgres:5432/postgres"
  TEST_DB_URL="sqlite:///:memory:"
EOF
