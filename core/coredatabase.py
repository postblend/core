# SPDX-FileCopyrightText: 2022 Claudio Cambra <developer@claudiocambra.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

import enum
import hashlib
import sqlite3
import warnings

from dataclasses import dataclass
from os import urandom
from os.path import exists

from core.api.v1.account import AccountId

SALT_LENGTH = 32
HASH_ITERATIONS = 100000

USERS_TABLE = "users"
ID_COLUMN = "id"
ACCOUNT_NAME_COLUMN = "name"
USERNAME_COLUMN = "username"
KEY_COLUMN = "key"
SALT_COLUMN = "salt"

@dataclass
class UserAccountData:
    id: AccountId
    account_name: str
    username: str
    key: str
    salt: str

@dataclass
class UserCredCheckResult(enum.Enum):
    UNKNOWN_USERNAME = 0
    INCORRECT_PASSWORD = 1
    CORRECT = 2

# Stores sensitive user data pertaining to platform accounts.
# Each platform must have a unique plugin id to be identified in the database.

class CoreDatabase:
    __instance = None

    @staticmethod
    def instance(db_path: str = None):
        if CoreDatabase.__instance == None:
            print("Creating new CoreDatabase instance.")
            CoreDatabase(str(db_path))
        elif db_path != None:
            warnings.warn("There is already a live database instance. Ignoring new database path and returning original instance.")

        return CoreDatabase.__instance

    def __init__(self, db_path: str):
        if CoreDatabase.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            CoreDatabase.__instance = self

        need_initial_setup = not exists(db_path)
        self._connection = sqlite3.connect(db_path)

        if need_initial_setup:
            print(f"File at {db_path} does not exist. Creating database with provided path.")

            print("Creating user accounts table...")
            query = f'''CREATE TABLE IF NOT EXISTS {USERS_TABLE}
                (
                    {ID_COLUMN}             INTEGER     PRIMARY KEY     AUTOINCREMENT,
                    {ACCOUNT_NAME_COLUMN}   TEXT,
                    {USERNAME_COLUMN}       TEXT        UNIQUE          NOT NULL,
                    {KEY_COLUMN}            TEXT,
                    {SALT_COLUMN}           TEXT
                );
                '''
            cursor = self._connection.cursor()
            cursor.execute(query)
            self._connection.commit()

    def __del__(self):
        if self._connection:
            self._connection.close()


    ########## UTILITY METHODS ##########

    def table_fields(self, table_name: str) -> list[str]:
        first_row_query = f"SELECT * FROM {table_name} LIMIT 1;"
        cursor = self._connection.cursor()
        cursor.execute(first_row_query)
        field_names = [description[0] for description in cursor.description]
        return field_names


    def user_exists(self, account_id: int) -> bool:
        print(f"Checking if user with {account_id} exists in database...")
        user_exists_query = f"SELECT 1 FROM {USERS_TABLE} WHERE {ID_COLUMN} = ?;"
        parameters = (account_id,)

        cursor = self._connection.cursor()
        return cursor.execute(user_exists_query, parameters).fetchone() != None


    def username_exists(self, username: str) -> bool:
        print(f"Checking if user {username} exists in database...")
        username_exists_query = f"SELECT 1 FROM {USERS_TABLE} WHERE {USERNAME_COLUMN} = ?;"
        parameters = (username,)

        cursor = self._connection.cursor()
        return cursor.execute(username_exists_query, parameters).fetchone() != None


    def valid_login(self, username: str, password: str) -> UserCredCheckResult:
        print(f"Checking if login details for user {username} are valid...")
        if not self.username_exists(username):
            return UserCredCheckResult.UNKNOWN_USERNAME

        query = f"SELECT {KEY_COLUMN}, {SALT_COLUMN} FROM {USERS_TABLE} WHERE {USERNAME_COLUMN} = ?;"
        parameters = (username,)
        cursor = self._connection.cursor()
        db_key, salt = cursor.execute(query, parameters).fetchone()

        given_password_hashed = self.hash_password(password, salt)

        if given_password_hashed == db_key:
            return UserCredCheckResult.CORRECT
        
        return UserCredCheckResult.INCORRECT_PASSWORD


    # ALWAYS HASH A PASSWORD BEFORE PUTTING IT INTO THE DATABASE. NEVER STORE A PASSWORD AS PLAIN TEXT.
    # We do NOT want to know a user's password. If we need to know a user's password, we don't.
    # All we need to know is how to compare the user's provided password with the one in the database.
    # This can just be done by hashing the provided password using the same salt and comparing the result.
    def hash_password(self, password: str, salt: bytes) -> bytes:
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, HASH_ITERATIONS)
        return key


    # Add a new user account for the given platform.
    def add_user_account(self, username: str, password: str, account_name: str = "", commit: bool = True) -> bool:
        print(f"Inserting user {username} into database...")
        if self.username_exists(username):
            print(f"User {username} already in database.")
            return False
        else:
            salt = urandom(SALT_LENGTH)
            hashed_password = self.hash_password(password, salt)
            # First null as is autoincrement id, let the db take care of it
            query = f"INSERT INTO {USERS_TABLE} VALUES (null, ?, ?, ?, ?);"
            parameters = (account_name, username, hashed_password, salt)

            cursor = self._connection.cursor()
            cursor.execute(query, parameters)

        if commit:
            self._connection.commit()
        
        return True


    # Make sure the password is hashed before you update the user account!
    def update_user_account(self, account_data: UserAccountData, commit: bool = True) -> bool:
        print(f"Updating data for user {account_data.username} in database...")
        if not self.user_exists(account_data.id):
            print(f"User {account_data.username} with id {account_data.id} not in database. Skipping.")
            return False
        else:
            query = f'''UPDATE {USERS_TABLE}
                SET
                    {ACCOUNT_NAME_COLUMN} = ?,
                    {USERNAME_COLUMN} = ?,
                    {KEY_COLUMN} = ?,
                    {SALT_COLUMN} = ?,
                WHERE {ID_COLUMN} = ?;
                '''
            parameters = (account_data.account_name, account_data.username, account_data.key, account_data.salt)

            cursor = self._connection.cursor()
            cursor.execute(query, parameters)

        if commit:
            self._connection.commit()
        
        return True


    def delete_user_account(self, account_data: UserAccountData, commit: bool = True) -> bool:
        print(f"Deleting user {account_data.username} from database...")
        if not self.user_exists(account_data.id):
            print(f"User {account_data.username} with id {account_data.id} not in database. Skipping delete.")
            return False
        else:
            delete_query = f"DELETE FROM {USERS_TABLE} WHERE {ID_COLUMN} = ?;"
            parameters = (account_data.id,)

            cursor = self._connection.cursor()
            cursor.execute(delete_query, parameters)
        
        if commit:
            self._connection.commit()
        
        return True
    

    #def user_groups

    #def create_user_group

    #def delete_user_group

    #def users_in_group

    #def add_user_to_group

    #def delete_user_from_group