from psycopg2 import pool


class Database:
    __connection_pool = None

    @classmethod
    def initialise(cls):
        cls.__connection_pool = pool.SimpleConnectionPool(10, 20, user='postgres', password='smpl@509',
                                                          database='smpl_prodn',
                                                          host='localhost')

    @classmethod
    def get_connection(cls):
        cls.initialise()
        return cls.__connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        Database.__connection_pool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        Database.__connection_pool.closeall()


# What this class does is returns a cursor from a connection pool. The init does not initialise a connection and cursor
# enter is run at the beginning of with, initialises connection with a connection from Database class, and gets a
# connection from connection pool, and returns the cursor from the connection pool
# Exit (if there is no exception) commits the changes and then closes the connection
class CursorFromConnectionFromPool:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = Database.get_connection()
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        # If there is some sort of exception, rollback, else commit
        if exc_val is not None:
            self.connection.rollback()
        else:
            self.cursor.close()
            self.connection.commit()
        Database.return_connection(self.connection)
