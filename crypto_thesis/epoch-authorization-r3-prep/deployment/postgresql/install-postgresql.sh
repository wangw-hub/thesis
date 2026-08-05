#!/usr/bin/env bash
set -Eeuo pipefail

export DEBIAN_FRONTEND=noninteractive
sudo -n apt-get update
sudo -n apt-get install -y postgresql postgresql-contrib python3-psycopg openssl

version="$(psql --version | awk '{print $3}')"
major="${version%%.*}"
conf="/etc/postgresql/${major}/main/postgresql.conf"
hba="/etc/postgresql/${major}/main/pg_hba.conf"
secret_dir="/etc/epoch-auth"
secret_file="${secret_dir}/postgres-password"

sudo -n install -d -m 0750 -o root -g postgres "${secret_dir}"
if ! sudo -n test -s "${secret_file}"; then
  umask 077
  password="$(openssl rand -base64 36 | tr -d '\n')"
  printf '%s' "${password}" | sudo -n tee "${secret_file}" >/dev/null
  sudo -n chown root:postgres "${secret_file}"
  sudo -n chmod 0640 "${secret_file}"
fi
password="$(sudo -n cat "${secret_file}")"

sudo -n sed -i "s/^#\\?listen_addresses\\s*=.*/listen_addresses = 'localhost,192.168.6.133'/" "${conf}"
sudo -n sed -i "s/^#\\?password_encryption\\s*=.*/password_encryption = 'scram-sha-256'/" "${conf}"
if ! sudo -n grep -q '^hostssl epoch_auth epoch_auth 192\.168\.6\.0/24 scram-sha-256$' "${hba}"; then
  printf '%s\n' 'hostssl epoch_auth epoch_auth 192.168.6.0/24 scram-sha-256' |
    sudo -n tee -a "${hba}" >/dev/null
fi

sudo -n systemctl restart postgresql
for _ in $(seq 1 24); do
  if sudo -n -u postgres pg_isready -q; then break; fi
  sleep 5
done
sudo -n -u postgres pg_isready -q

sudo -n -u postgres psql -v ON_ERROR_STOP=1 \
  --set=app_password="${password}" <<'SQL' >/dev/null
SELECT format('CREATE ROLE epoch_auth LOGIN PASSWORD %L', :'app_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'epoch_auth')\gexec
SELECT format('ALTER ROLE epoch_auth PASSWORD %L', :'app_password')\gexec
SELECT 'CREATE DATABASE epoch_auth OWNER epoch_auth'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'epoch_auth')\gexec
SQL

sudo -n -u postgres psql -v ON_ERROR_STOP=1 -d epoch_auth -c \
  'ALTER SCHEMA public OWNER TO epoch_auth' >/dev/null

printf 'postgresql_version=%s\n' "${version}"
printf 'config=%s\n' "${conf}"
printf 'hba=%s\n' "${hba}"
printf 'secret_file=%s\n' "${secret_file}"
printf 'listen=localhost,192.168.6.133\n'
