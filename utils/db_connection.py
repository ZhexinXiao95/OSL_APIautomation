import mysql.connector
from mysql.connector import Error
from typing import Any, List, Tuple

from utils.ini_read import read_pytest_ini
from utils.log import logger


class Database:
    def __init__(self):
        self.env = read_pytest_ini('env', 'global setting')
        self.database_connection_data = read_pytest_ini('database', self.env)

    def __enter__(self):
        logger.log(f'<----- {self.env} Database connecting ----->')
        self.connection = mysql.connector.connect(
            host=self.database_connection_data[0],
            user=self.database_connection_data[1],
            password=self.database_connection_data[2]
        )
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
        logger.log(f'<----- {self.env} Database disconnecting ----->')

    def execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> None:
        self.cursor.execute(query, params)
        self.connection.commit()

    def fetch_all(self, query: str, params: Tuple[Any, ...] = ()) -> List[Tuple[Any, ...]]:
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query: str, params: Tuple[Any, ...] = ()) -> Tuple[Any, ...]:
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def run_sql(self, command):
        with Database() as db:
            try:
                users = db.fetch_all(command)
                logger.log(f'<----- Data found -----> {command}')
                return users
            except Error as e:
                logger.log(f"An error occurred: {e}",'critical')


# 示例用法
if __name__ == "__main__":
    print(Database().run_sql("select * from dragoncoin.user where uuid = 'bc3ce5c2-afaf-4597-a8a8-eb14886ad1e0'"))
