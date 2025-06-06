import pymysql


class Database:
    def __init__(self, *,
                 host: str = 'localhost',
                 port: int = 3306,
                 user: str = 'admin',
                 password: str = 'admin',
                 database: str = 'database',
                 autoreconnect: bool = False,
                 autocommit: bool = True):

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.autoreconnect = autoreconnect
        self.autocommit = autocommit

        self.cursor = None
        self.connection = None

    def connect(self):
        try:
            if self.get_status:
                self.connection.close()
        except:
            pass
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=self.autocommit
        )
        self.cursor = self.connection.cursor()

    def get_status(self, *args):
        if not self.connection: return False
        if self.connection.open: return True
        return False

    def get_fields(self, table_name):
        self.cursor.execute("SELECT COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %s", (table_name,))
        return [column["COLUMN_NAME"] for column in self.cursor.fetchall()]
