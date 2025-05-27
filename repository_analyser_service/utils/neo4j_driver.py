from neo4j import GraphDatabase
import os

class Neo4j:
    def __init__(self):
        self.__driver = None

    def connect(self):

        AUTH = (os.environ.get('NEO4j_USERNAME'), os.environ.get('NEO4j_PASSWORD'))
        self.__driver = GraphDatabase.driver(os.environ.get('NEO4j_URI'), auth=AUTH, connection_acquisition_timeout=2, connection_timeout=1, liveness_check_timeout=251, max_connection_lifetime=240)
        return self.__driver

    @property
    def driver(self):
        if not self.__driver:
            return self.connect()
        return self.__driver

neo4j_driver = Neo4j()