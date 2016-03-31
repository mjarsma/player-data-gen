"""
A wrapper for pymongo. Using a shared connection instead of a singleton pattern.
"""

from pymongo import MongoClient


class Connection(object):
    """
    Create pymongo connection.
    The @classmethod requires a reference to a class object as the first parameter.
    """

    instance = None
    connection = None
    db = None

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = Connection()
        return cls._instance

    def connect(self, uri):
        """
        Establish a mongodb connection and return it.
        """
        conn = self.instance()
        conn.connection = MongoClient(uri)
        return conn.connection

    def disconnect(self):
        self.close

    def get_database(self, db):
        """
        Retrieve the connection from an existing instance or create a new one.
        """
        return self.connection.db




def connect(*args, **kwargs):
    """
    Initializes a connection and the database. It returns
    the pymongo connection object so that end_request, etc.
    can be called if necessary.
    """
    return Connection.connect(*args, **kwargs)

