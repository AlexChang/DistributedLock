import utils as F
import parameter as P
import RWLock

import socket
import multiprocessing
import logging
import json

logger = logging.getLogger('main' + '.' + __name__)

class Client:

    def __init__(self, ip=P.LOCALHOST):
        self.ip = ip
        self.uuid = F.generate_uuid()
        self.server = None

    def get_addr(self):
        return '{}'.format(self.ip)

    def get_short_uuid(self, length=-8):
        return '{}'.format(self.uuid[length:])

    def get_uuid_and_addr(self):
        return '{}({})'.format(self.get_short_uuid(), self.get_addr())

    def add_corresponding_server(self, server):
        self.server = server
        logger.info('Assign server {} as the corresponding server of client {}'.format(
            self.server.get_short_uuid(), self.get_short_uuid()))

    def try_lock(self, lock_key):
        logger.info('Client {} performing "try_lock" operation with lock_key = "{}"'.format(
            self.get_short_uuid(), lock_key))

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server.ip, self.server.port))
        request_data = {'type': 'client', 'op': 'try_lock', 'args': {'lock_key': lock_key, 'client_id': self.uuid}}
        encoded_request_data = json.dumps(request_data).encode('utf-8')
        client_socket.send(encoded_request_data)
        received_data = json.loads(client_socket.recv(1024).decode())
        client_socket.close()

        logger.info('Client {} operation "try_lock" with lock_key = "{}" result: {}'.format(
            self.get_short_uuid(), lock_key, received_data))

    def try_unlock(self, lock_key):
        logger.info('Client {} performing "try_unlock" operation with lock_key = "{}"'.format(
            self.get_short_uuid(), lock_key))

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server.ip, self.server.port))
        request_data = {'type': 'client', 'op': 'try_unlock', 'args': {'lock_key': lock_key, 'client_id': self.uuid}}
        encoded_request_data = json.dumps(request_data).encode('utf-8')
        client_socket.send(encoded_request_data)
        received_data = json.loads(client_socket.recv(1024).decode())
        client_socket.close()

        logger.info('Client {} operation "try_unlock" with lock_key = "{}" result: {}'.format(
            self.get_short_uuid(), lock_key, received_data))

    def own_the_lock(self, lock_key):
        logger.info('Client {} performing "own_the_lock" operation with lock_key = "{}"'.format(
            self.get_short_uuid(), lock_key))

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server.ip, self.server.port))
        request_data = {'type': 'client', 'op': 'own_the_lock', 'args': {'lock_key': lock_key, 'client_id': self.uuid}}
        encoded_request_data = json.dumps(request_data).encode('utf-8')
        client_socket.send(encoded_request_data)
        received_data = json.loads(client_socket.recv(1024).decode())
        client_socket.close()

        logger.info('Client {} operation "own_the_lock" with lock_key = "{}" result: {}'.format(
            self.get_short_uuid(), lock_key, received_data))