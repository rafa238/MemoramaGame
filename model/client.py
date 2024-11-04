class Client:
    def __init__(self, name, host, port, sock):
        self.name = name
        self.host = host
        self.port = port
        self.sock = sock
