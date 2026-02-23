import time
from typing import Any

from warg import AlsoDecorator

__all__ = ["QliveClient"]

DEFAULT_PORT = "5555"


def default_address() -> str:
    """

    :return:
    :rtype:
    """
    from draugr.python_utilities import in_docker

    if in_docker():
        return f"tcp://host.docker.internal:{DEFAULT_PORT}"
    return f"tcp://localhost:{DEFAULT_PORT}"


class QliveClient(AlsoDecorator):
    """
    TODO: MAYBE NOT ALSO A DECORATOR

    Client for sending data to qgis instance
    """

    def __init__(self, address: str = default_address()):
        import zmq

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)

        if not address:
            address = default_address()

        if str.isnumeric(address):  # only port was given
            address = f"{default_address().split(f':{DEFAULT_PORT}')[0]}:{address}"

        if "tcp://" not in address:  # protocol is missing
            address = f"tcp://{address}"

        self.address = address

        self.blocking = False
        self.flag = None
        if not self.blocking:
            self.poller = zmq.Poller()
            self.flag = zmq.NOBLOCK
            self.wait_time = 1000
            self.poller.register(self.socket, zmq.POLLIN)

    def __enter__(self):
        self.socket.connect(self.address)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.close()

    def send(self, *args) -> Any:
        """

        :param args:
        :type args:
        :return:
        :rtype:
        """
        import zmq

        self.socket.send(*args, self.flag)

        time.sleep(0.1)  # TODO: TEMPORARY WORKAROUND! for state fail

        if self.blocking:
            return self.socket.recv()

        socks = dict(self.poller.poll(self.wait_time))
        if socks:
            if socks.get(self.socket) == zmq.POLLIN:
                return self.socket.recv(self.flag)

        return  # TODO: just ignore for now
        raise TimeoutError
