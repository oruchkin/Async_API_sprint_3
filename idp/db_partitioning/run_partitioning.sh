#!/bin/bash

ENV_FILE="../.env"

export $(grep -v '^#' $ENV_FILE | xargs)

POSTGRES_HOST="localhost"
POSTGRES_DB="postgres"

PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -f partitioning.sql

if [ $? -eq 0 ]; then
    echo "Partitioning script executed successfully."
else
    echo "Failed to execute partitioning script."
    exit 1
fi
