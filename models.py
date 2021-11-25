import argparse
import hashlib
import random
import string

import psycopg2
from psycopg2 import connect, errors

# Alphabet:
ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase

# ArgParse:
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", help="Input username")
parser.add_argument("-p", "--password", help="Input password")
parser.add_argument("-n", "--newpass", help="Input new password")
parser.add_argument("-l", "--list", help="Listing all users", action="store_true")
parser.add_argument("-d", "--delete", help="Delete user by ID")
parser.add_argument("-e", "--edit", help="Edit user by ID", action="store_true")
args = parser.parse_args()


# Connecting:
conn = connect(user="postgres", password="coderslab", host="localhost", port=8888, database="workshop")
conn.autocommit = True
cur = conn.cursor()


# Password:
def hash_password(password, salt=None):
    """
    Hashes the password with salt as an optional parameter.

    If salt is not provided, generates random salt.
    If salt is less than 16 chars, fills the string to 16 chars.
    If salt is longer than 16 chars, cuts salt to 16 chars.

    :param str password: password to hash
    :param str salt: salt to hash, default None

    :rtype: str
    :return: hashed password
    """

    # generate salt if not provided
    if salt is None:
        salt = generate_salt()

    # fill to 16 chars if too short
    if len(salt) < 16:
        salt += ("a" * (16 - len(salt)))

    # cut to 16 if too long
    if len(salt) > 16:
        salt = salt[:16]

    # use sha256 algorithm to generate haintegersh
    t_sha = hashlib.sha256()

    # we have to encode salt & password to utf-8, this is required by the
    # hashlib library.
    t_sha.update(salt.encode('utf-8') + password.encode('utf-8'))

    # return salt & hash joined
    return salt + t_sha.hexdigest()


def check_password(pass_to_check, hashed):
    """
    Checks the password.
    The function does the following:
        - gets the salt + hash joined,
        - extracts salt and hash,
        - hashes `pass_to_check` with extracted salt,
        - compares `hashed` with hashed `pass_to_check`.
        - returns True if password is correct, or False. :)

    :param str pass_to_check: not hashed password
    :param str hashed: hashed password

    :rtype: bool
    :return: True if password is correct, False elsewhere
    """

    # extract salt
    salt = hashed[:16]

    # extract hash to compare with
    hash_to_check = hashed[16:]

    # hash password with extracted salt
    new_hash = hash_password(pass_to_check, salt)

    # compare hashes. If equal, return True
    return new_hash[16:] == hash_to_check


def generate_salt():
    """
    Generates a 16-character random salt.

    :rtype: str
    :return: str with generated salt
    """
    salt = ""
    for i in range(0, 16):

        # get a random element from the iterable
        salt += random.choice(ALPHABET)
    return salt


class User:
    def __init__(self, username="", password="", salt=None):
        self._id = -1
        self.username = username
        self._hashed_password = hash_password(password, salt)

    @property
    def id(self):
        return self._id

    @property
    def hashed_password(self):
        return self._hashed_password

    def set_password(self, password, salt=""):
        self._hashed_password = hash_password(password, salt)

    @hashed_password.setter
    def hashed_password(self, password):
        self.set_password(password)

    def save_to_db(self):
        if self._id == -1:
            sql = "INSERT INTO users(username, hashed_password) VALUES (%s, %s) RETURNING id"
            values = (self.username, self.hashed_password)
            cur.execute(sql, values)
            self._id = cur.fetchone()[0]
            return True
        return False

    @staticmethod
    def load_user_by_id(id_):
        sql = """SELECT id, username, hashed_password FROM users WHERE id = %s"""
        cur.execute(sql, (id_,))
        data = cur.fetchone()
        if data:
            id_, username, hashed_password = data
            loaded_user = User(username)
            loaded_user._id = id_
            loaded_user._hashed_password = hashed_password
            return loaded_user
        else:
            return None

    @staticmethod
    def load_user_by_username(username):
        sql = "SELECT id, username, hashed_password FROM users WHERE username = '" + username + "'"
        cur.execute(sql, username)
        data = cur.fetchone()
        if data:
            id_, username, hashed_password = data
            loaded_user = User(username)
            loaded_user._id = id_
            loaded_user._hashed_password = hashed_password
            return loaded_user
        else:
            return None

    @staticmethod
    def load_all_users():
        sql = """SELECT id, username, hashed_password FROM users"""
        cur.execute(sql)
        data = cur.fetchone()
        if data:
            id_, username, hashed_password = data
            loaded_user = User(username)
            loaded_user._id = id_
            loaded_user._hashed_password = hashed_password
            return loaded_user
        else:
            return None

    @staticmethod
    def delete_user_by_id(id_):
        sql = """DELETE FROM users WHERE id = %s"""
        cur.execute(sql, (id_,))
        User._id = -1


class Messages:
    def __init__(self, from_id, to_id, text):
        self._id = -1
        self.from_id = from_id
        self.to_id = to_id
        self.text = text
        self.creation_date = None

    @property
    def id(self):
        return self._id

    def save_to_db(self):
        sql = """INSERT INTO messages(from_id, to_id, text) VALUES (%s, %s, %s)"""
        values = (self.from_id, self.to_id, self.text)
        cur.execute(sql, values)

    @staticmethod
    def load_all_messages():
        sql = """SELECT id, from_id, to_id, creation_date, text FROM messages"""
        cur.execute(sql)
        data = cur.fetchone()
        if data:
            id_, from_id, to_id, creation_date, text = data
            loaded_message = Messages(from_id, to_id, text)
            loaded_message.from_id = from_id
            loaded_message.to_id = to_id
            loaded_message.text = text
            return loaded_message
        else:
            return None

    # Creating user, handling exception, checking password length
    try:
        if args.username and args.password is not None and args.edit and args.newpass is None:
            if len(args.password) >= 8:
                # noinspection PyTypeChecker
                x = args.username
                x = User(args.username, args.password)
                x.save_to_db()
            elif len(args.password) < 8:
                print("==Password is too short (must be 8 characters long)==")
    except psycopg2.errors.UniqueViolation as ex:
        print("\n==User already exist==")

    # Edit password
    if args.username and args.password and args.edit and args.newpass is not None:
        # Checking if user is created:
        sql = (f"SELECT username FROM users WHERE username =  '{args.username}'")
        cur.execute(sql)
        # If existing:
        if cur.fetchall() is not None:
            password_sql = (f"SELECT hashed_password FROM users WHERE username = '{args.username}'")
            cur.execute(password_sql)
            data = cur.fetchone()
            data = str(data)
            # Hopefully Checking if password is proper
            # !!!!!!!!!!!!!!! Nie da się zalogować, poprawię jutro:)
            if check_password(args.password, data) is True:
                # Checking password length
                if len(args.newpass) >= 8:
                    # noinspection PyTypeChecker
                    newpass = args.newpass
                    newpass = hash_password(newpass)
                    set_newpass = (f"UPDATE users SET hashed_password = '{newpass}' WHERE username = '{args.username}'")
                    cur.execute(set_newpass)
                    print("==New password setted==")
                elif len(args.newpass) < 8:
                    print("==New password is too short (must be 8 characters long)==")
            else:
                print("==Wrong password!==")
        # If not:
        else:
            print("==User doesn't exist==")

