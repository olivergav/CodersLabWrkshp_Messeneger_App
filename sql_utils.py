# """Module to connect with SQL Database"""
from psycopg2 import connect, DatabaseError, OperationalError


# Connect to DB
USER = "postgres"
HOST = "localhost"
PASSWORD = "coderslab"
DB = "workshop"


def execute_sql(sql_code):
    try:
        with connect(user=USER, password=PASSWORD, host=HOST, port=8888, database=DB) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(sql_code)
                if cur.description:
                    return list(cur)
    except DatabaseError or OperationalError as ex:
        print(f"Błąd zapytania: {ex}")
        raise
