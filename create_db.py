from psycopg2 import connect, DatabaseError, OperationalError, errors
# Tworzenie obiektu kursora:


conn = connect(user="postgres", password="coderslab", host="localhost", port=8888, database="workshop")
conn.autocommit = True
cur = conn.cursor()


def create_database():
    try:
        name = str(input("Podaj nazwę bazy danych, którą chcesz stworzyć: "))
        cur.execute(f"CREATE DATABASE {name}")
    except errors.DuplicateDatabase as ex:
        print("Błąd zapytania: ", ex)


def create_table_user():
    try:
        cur.execute("""CREATE TABLE users(id SERIAL PRIMARY KEY, username VARCHAR(255), hashed_password varchar(80));""")
    except errors.DuplicateTable as ex:
        print("Błąd zapytania: ", ex)


def create_table_messages():
    try:
        cur.execute("""CREATE TABLE messages(id SERIAL PRIMARY KEY, from_id INT, to_id INT, creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, text VARCHAR(255))""")
        cur.execute("""ALTER TABLE messages ADD FOREIGN key (from_id) REFERENCES users(id)""")
        cur.execute("""ALTER TABLE messages ADD FOREIGN key (to_id) REFERENCES users(id)""")
    except errors.DuplicateTable as ex:
        print("Błąd zapytania: ", ex)


def creating():
    try:
        create_cursor_n_connect()
        # create_database()
        create_table_user()
        create_table_messages()
    except OperationalError as ex:
        print("Błąd zapytania: ", ex)
        raise

# Chcąc wywołać wszystkie funkcje, wywołaj funkcję "creating()"
# creating()
