import socket
import time
import logging


class Protocol:

    def __init__(self, server, port=6667):
        self.connection = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        try:
            self.connection.connect((server, port))
        except socket.gaierror:
            raise RuntimeError('unknown host "{0}"'.format(server))

    def send(self, message):
        """
        send chunks of the message until the entire
        message has been sent to the server
        """
        logging.debug("send: " + message.strip())

        datasent = 0
        message += "\n"

        while datasent < len(message):
            sent = self.connection.send(message.encode())
            if sent == 0:
                raise RuntimeError("connection reset by peer")
            else:
                datasent += sent

    def recv(self):
        """
        receive data from the server until
        we have received the end of the message
        """

        data = ""

        while "\r" not in data:
            try:
                chunk = self.connection.recv(512).decode()
            except TimeoutError:
                raise RuntimeError("connection timed out")
            if chunk is None:
                raise RuntimeError("connection reset by peer")
            else:
                data += chunk

        logging.debug("receive: " + data.strip())

        return data

    def join(self, channel):
        self.send("JOIN " + channel)

    def notice(self, nickname, text):
        self.send("NOTICE {0} :{1}".format(nickname, text))

    def privmsg(self, reciever, message):
        self.send("PRIVMSG {0} :{1}".format(reciever, message))

    def topic(self, channel, topic):
        self.send("TOPIC {0} :{1}".format(channel, topic))

    def identify(self, username):
        self.send("USER {0} localhost localhost :{1}".format(
            username, username))
        self.send("NICK " + username)

    def whois(self, nickname):
        """
        pull whois data from server
        """

        self.send("WHOIS " + nickname)

        data = ""
        while "End of WHOIS" not in data:
            data += self.recv()
        return data

    def disconnect(self, message="disconnect"):
        self.send("QUIT :" + message)
        # time.sleep(5.0)
        # self.connection.shutdown(socket.SHUT_RDWR)
        # self.connection.close()
