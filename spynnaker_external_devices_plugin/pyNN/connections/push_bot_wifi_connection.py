from spinnman.connections.abstract_classes.abstract_listenable import \
    AbstractListenable
from spinnman.exceptions import SpinnmanIOException
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.connections.abstract_classes.abstract_connection \
    import AbstractConnection

import platform
import subprocess
import socket
import select


class PushBotWIFIConnection(AbstractConnection, AbstractListenable):

    def __init__(self, local_host=None, local_port=56000):
        """
        :param local_host: The local host name or ip address to bind to.\
                    If not specified defaults to bind to all interfaces,\
                    unless remote_host is specified, in which case binding is\
                    _done to the ip address that will be used to send packets
        :type local_host: str or None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    setting up the communication channel
        """

        self._socket = None
        try:

            # Create a UDP Socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        except Exception as exception:
            raise SpinnmanIOException(
                "Error setting up socket: {}".format(exception))

        # Get the port to bind to locally
        local_bind_port = 0
        if local_port is not None:
            local_bind_port = int(local_port)

        # Get the host to bind to locally
        local_bind_host = ""
        if local_host is not None:
            local_bind_host = str(local_host)

        try:
            # Bind the socket
            self._socket.connect((local_bind_host, local_bind_port))

        except Exception as exception:
            raise SpinnmanIOException(
                "Error binding socket to {}:{}: {}".format(
                    local_bind_host, local_bind_port, exception))

        # Mark the socket as non-sending, unless the remote host is
        # specified - send requests will then cause an exception
        self._can_send = True

        # Get the details of where the socket is connected
        self._local_ip_address = None
        self._local_port = None
        try:
            self._local_ip_address, self._local_port =\
                self._socket.getsockname()

            # Ensure that a standard address is used for the INADDR_ANY
            # hostname
            if self._local_ip_address is None or self._local_ip_address == "":
                self._local_ip_address = "0.0.0.0"
        except Exception as exception:
            raise SpinnmanIOException("Error querying socket: {}".format(
                exception))

        # Set a general timeout on the socket
        self._socket.settimeout(0)

    def is_connected(self):
        """ See\
            :py:meth:`spinnman.connections.AbstractConnection.abstract_connection.is_connected`
        """

        # If this is not a sending socket, it is not connected
        if not self._can_send:
            return False

        # check if machine is active and on the network
        pingtimeout = 5
        while pingtimeout > 0:

            # Start a ping process
            process = None
            if platform.platform().lower().startswith("windows"):
                process = subprocess.Popen(
                    "ping -n 1 -w 1 " + self._remote_ip_address,
                    shell=True, stdout=subprocess.PIPE)
            else:
                process = subprocess.Popen(
                    "ping -c 1 -W 1 " + self._remote_ip_address,
                    shell=True, stdout=subprocess.PIPE)
            process.wait()

            if process.returncode == 0:

                # ping worked
                return True
            else:
                pingtimeout -= 1

        # If the ping fails this number of times, the host cannot be contacted
        return False

    @property
    def local_ip_address(self):
        """ The local IP address to which the connection is bound.

        :return: The local ip address as a dotted string e.g. 0.0.0.0
        :rtype: str
        :raise None: No known exceptions are thrown
        """
        return self._local_ip_address

    @property
    def local_port(self):
        """ The local port to which the connection is bound.

        :return: The local port number
        :rtype: int
        :raise None: No known exceptions are thrown
        """
        return self._local_port

    @property
    def remote_ip_address(self):
        """ The remote ip address to which the connection is connected.

        :return: The remote ip address as a dotted string, or None if not\
                    connected remotely
        :rtype: str
        """
        return self._remote_ip_address

    @property
    def remote_port(self):
        """ The remote port to which the connection is connected.

        :return: The remote port, or None if not connected remotely
        :rtype: int
        """
        return self._remote_port

    def receive(self, timeout=None):
        """ Receive data from the connection

        :param timeout: The timeout, or None to wait forever
        :type timeout: None
        :return: The data received
        :rtype: bytestring
        :raise SpinnmanTimeoutException: If a timeout occurs before any data\
                    is received
        :raise SpinnmanIOException: If an error occurs receiving the data
        """
        try:
            self._socket.settimeout(timeout)
            return self._socket.recv(1024)
        except socket.timeout:
            raise SpinnmanTimeoutException("receive", timeout)
        except Exception as e:
            raise SpinnmanIOException(str(e))

    def send(self, data):
        """ Send data down this connection

        :param data: The data to be sent
        :type data: bytestring
        :raise SpinnmanIOException: If there is an error sending the data
        """
        if not self._can_send:
            raise SpinnmanIOException(
                "Remote host and/or port not set - data cannot be sent with"
                " this connection")
        try:
            self._socket.send(data)
        except Exception as e:
            raise SpinnmanIOException(str(e))

    def close(self):
        """ See\
            :py:meth:`spinnman.connections.abstract_connection.AbstractConnection.close`
        """
        try:
            self._socket.shutdown(socket.SHUT_WR)
        except:
            pass
        self._socket.close()

    def is_ready_to_receive(self, timeout=0):
        return len(select.select([self._socket], [], [], timeout)[0]) == 1

    def get_receive_method(self):
        return self.receive