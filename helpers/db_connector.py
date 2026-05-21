import psycopg2
import os



pg_pwd = os.getenv("POSTGRES_PW")
pg_usr = os.getenv("POSTGRES_USER")
pg_host = os.getenv("POSTGRES_HOST")
pg_port = os.getenv("POSTGRES_PORT")


def postgress_connection():
    conn = psycopg2.connect(
            database="postgres",
            user=pg_usr,
            password=pg_pwd,
            host=pg_host,
            port=pg_port
        )

    return conn
