import utils as F

import multiprocessing
import logging

logger = logging.getLogger('main' + '.' + __name__)

class Client:

    def __init__(self, ip):
        self.ip = ip
        self.uuid = F.generate_uuid_by_ip(self.ip)
        self.server = None
        self.connection_to_server = None

    def __str__(self):
        description = "Client: {}\nip: {}\nserver: {}\n".format(self.uuid, self.ip, self.server.uuid)
        return description

    def add_corresponding_server(self, server):
        self.server = server

    def establish_connections_to_server(self):
        logger.info('Establishing connection between client {}({}) and server {}({})...'.format(
            self.uuid, self.ip, self.server.uuid, self.server.ip))
        conn1, conn2 = multiprocessing.Pipe()
        self.connection_to_server = conn1
        self.server.connection_to_client = conn2
        logger.info('Connection establishment completed!')

    # def try_lock(self, lock_key):
    #     logger.info('Client: {}({}) performing "try_lock" operation with lock_key = "{}"'.format(
    #         self.uuid, self.ip, lock_key))
    #     result = self.server.preempt_lock(lock_key, self.uuid)
    #     logger.info('client operation "try_lock" result: {}\n'.format(result))

    def try_lock(self, lock_key):
        logger.info('Client {}({}) performing "try_lock" operation with lock_key = "{}"'.format(
            self.uuid, self.ip, lock_key))
        logger.debug('Client {}({}) sending request to server {}({})'.format(
            self.uuid, self.ip, self.server.uuid, self.server.ip))
        self.connection_to_server.send(lock_key)
        logger.debug('Client {}({}) fetching operation result from server {}({})'.format(
            self.uuid, self.ip, self.server.uuid, self.server.ip))
        result = self.connection_to_server.recv()
        logger.info('Client {}({}) operation "try_lock" result: {}\n'.format(
            self.uuid, self.ip, result))

    def try_unlock(self, lock_key):
        logger.info('Client: {}({}) performing "try_unlock" operation with lock_key = "{}"'.format(
            self.uuid, self.ip, lock_key))
        result = self.server.release_lock(lock_key, self.uuid)
        logger.info('Client {}({}) operation "try_unlock" result: {}\n'.format(
            self.uuid, self.ip, result))

    def own_the_lock(self, lock_key):
        logger.info('Client: {}({}) performing "own_the_lock" operation with lock_key = "{}"'.format(
            self.uuid, self.ip, lock_key))
        result = self.server.check_lock(lock_key, self.uuid)
        logger.info('Client {}({}) operation "own_the_lock" result: {}\n'.format(
            self.uuid, self.ip, result))