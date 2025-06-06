from .monitoring import Server, ServerException

class server_:
    def __init__(self, host: str, port: int = 22003):
        self.host = host
        self.port = port
        self.server = None

    def connect(self):
        try:
            self.server = Server(self.host, self.port)
        except ServerException:
            self.server = None

    def reconnect(self):
        self.connect()
        if self.server: return True
        return False
