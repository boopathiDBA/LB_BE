import psycopg2
from app.helpers.log import logger

from app.settings import SConfig


class WebDBHelper:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WebDBHelper, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        sconfig = SConfig()
        sconfig.init_webdb_secrets()

        self.dbname = sconfig.webdb_secrets.get("dbname", "postgres")
        self.user = sconfig.webdb_secrets.get("username", "postgres")
        self.password = sconfig.webdb_secrets.get("password", "postgres")
        self.host = sconfig.webdb_secrets.get("host", "localhost")
        self.port = int(sconfig.webdb_secrets.get("port", 5432))
        self.connection = None
        err, errmsg = self.connect()
        if err:
            raise Exception(errmsg)

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            return False, None
        except Exception as e:
            return True, str(e)

    def disconnect(self):
        if self.connection:
            self.connection.close()
            logger.debug("Disconnected from Web DB")

    def select_one(self, query, values=None):
        try:
            with self.connection.cursor() as cursor:
                if values:
                    cursor.execute(query, values)
                else:
                    cursor.execute(query)
                result = cursor.fetchone()
                return result, False, None
        except Exception as e:
            return None, True, str(e)
