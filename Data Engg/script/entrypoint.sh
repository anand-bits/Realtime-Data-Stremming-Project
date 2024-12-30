#!/bin/bash
set -e

# Install Python packages from requirements.txt if it exists
if [ -e "/opt/airflow/requirements.txt" ]; then
  $(command -v pip) install --user -r /opt/airflow/requirements.txt
fi

# Initialize Airflow DB if not already initialized, and create the admin user
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

# Ensure the DB schema is up-to-date
$(command -v airflow) db upgrade

# Start the Airflow webserver
exec airflow webserver
