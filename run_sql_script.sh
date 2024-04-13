#!/bin/bash

DB_HOST="db"
DB_PORT="5432"
DB_NAME="bannerdb"
DB_USER="postgres"
DB_PASSWORD="12345"

SQL_SCRIPT="/code/init_triggers.sql"

COMMAND="psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f $SQL_SCRIPT"

export PGPASSWORD="$DB_PASSWORD"

$COMMAND
