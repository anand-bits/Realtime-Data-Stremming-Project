#!/bin/bash
set -e

# Install Python packages from requirements.txt if it exists
if [ -e "/opt/airflow/requirements.txt" ]; then
  $(command -v pip) install --no-cache-dir --user -r /opt/airflow/requirements.txt
fi

# Initialize Airflow DB and create admin user if needed
if [ ! -f "/opt/airflow/airflow.db" ]; then
  airflow db init && \
  airflow users create \
    --username admin \
    --firstname admin \
    --lastname admin \
    --role Admin \
    --email admin@example.com \
    --password admin
fi

# Upgrade Airflow DB schema to the latest version
$(command -v airflow) db upgrade

# Start the Airflow webserver
exec $(command -v airflow) webserver