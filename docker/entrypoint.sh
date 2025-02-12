#!/bin/bash

# Exit the script if any command fails
set -o errexit

# Exit the script if any command in a pipeline fails
set -o pipefail

# Exit the script if any undefined variable is used
set -o nounset

mysql_ready() {
python << END
import sys
import mysql.connector
from mysql.connector import Error

connection = None

try:
    connection = mysql.connector.connect(
        database="${MYSQL_NAME}",
        user="${MYSQL_USER}",
        password="${MYSQL_PASSWORD}",
        host="${MYSQL_HOST}",
        port="3306",
    )

    if connection:
        db_info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_info)

except Error as e:
    print("Error while connecting to MySQL", e)
    sys.exit(-1)
    
sys.exit(0)
END
}

# Loop until mysql_ready returns a success
until mysql_ready; do
 >&2 echo "Waiting for MySQL to become available....:-("
 sleep 2
done
>&2 echo "MySQL is ready!!..."

# Execute the provided command (e.g., start a service)
exec "$@"
