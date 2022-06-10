from gremlin_python.driver.transport import AbstractBaseTransport
import websocket


class WebsocketTransport(AbstractBaseTransport):

    def __init__(self, **kwargs):
        self.ws = websocket.WebSocket(**kwargs)

    def connect(self, url, headers=None):
        headers = headers or []
        self.ws.connect(url, header=headers)

    def write(self, message):
        self.ws.send_binary(message)

    def read(self):
        return self.ws.recv()

    def close(self):
        self.ws.close()

    @property
    def closed(self):
        return not self.ws.connected


def transport_factory():
    return WebsocketTransport()

