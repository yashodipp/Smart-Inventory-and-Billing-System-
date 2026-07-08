# Database Connection Settings
import getpass
import os

import psycopg2
from psycopg2 import OperationalError


def load_env_file(path=".env"):
    if not os.path.exists(path):
        return

    with open(path) as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def connection():
    load_env_file()

    config = {
        "host": os.getenv("PGHOST", "localhost"),
        "database": os.getenv("PGDATABASE", "ecommerce"),
        "user": os.getenv("PGUSER") or getpass.getuser(),
        "port": os.getenv("PGPORT", "5432"),
    }

    password = os.getenv("PGPASSWORD")
    if password:
        config["password"] = password

    try:
        con = psycopg2.connect(**config)
    except OperationalError as error:
        raise OperationalError(
            "Could not connect to PostgreSQL. Check that the database exists "
            "and set PGDATABASE, PGUSER, PGPASSWORD, PGHOST, or PGPORT if your "
            "local setup uses different credentials."
        ) from error

    con.autocommit = True

    print(
        f"Connection successful: database={config['database']} "
        f"user={config['user']}"
    )
    return con


conn = connection()
