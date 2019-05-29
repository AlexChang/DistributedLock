import utils as F
import parameter as P
import const as C
import rw_lock

import json
import socket
import threading
import logging
import select

logger = logging.getLogger('main' + '.' + __name__)


class Follower:

    def __init__(self, port, ip=C.LOCALHOST):
        self.ip = ip
        self.port = port
        self.uuid = F.generate_uuid_by_addr(self.get_addr())
        self.lock_map = {}
        self.leader = None
        self.stop_server = False
        self.mutex = threading.Lock()
        self.rwlock = rw_lock.RWLock()
        self.lock_type = P.lock_type
        self.consensus_type = P.consensus_type

    def get_addr(self):
        return '{}:{}'.format(self.ip, self.port)

    def get_short_uuid(self, length=-8):
        return '{}'.format(self.uuid[length:])

    def get_uuid_and_addr(self):
        return '{}({})'.format(self.get_short_uuid(), self.get_addr())

    def update_lock_map(self, lock_map):
        self.lock_map = lock_map

    def add_leader(self, leader):
        self.leader = leader

    def init_server(self):
        logger.info('Initializing server {}...'.format(self.get_uuid_and_addr()))
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.ip, self.port))
        server.listen(P.server_max_listen)
        while not self.stop_server:
            logger.debug('Server {} listening on {}...'.format(self.get_short_uuid(), self.get_addr()))
            r, _, _ = select.select([server], [], [], P.server_time_out)
            if r:
                conn, addr = server.accept()
                logger.debug('Server {} receives a connection from {}:{}'.format(self.get_short_uuid(), *addr))
                threading.Thread(target=self.handle_request, args=(conn, addr)).start()
        logger.info('Server {} has been shut down!'.format(self.get_short_uuid()))

    def handle_request(self, conn, addr):
        received_data = json.loads(conn.recv(1024).decode())
        logger.debug('Server {} receives data {}'.format(self.get_short_uuid(), received_data))
        if received_data['type'] == 'client':
            result = self.handle_client_request(received_data['op'], received_data['args'])
        elif received_data['type'] == 'server':
            result = self.handle_server_request(received_data['op'], received_data['args'])
        elif received_data['type'] == 'close':
            self.stop_server = True
            result = None
        else:
            logger.error('Unsupported request type {}'.format(received_data['type']))
            result = None
        encoded_result = json.dumps(result).encode('utf-8')
        conn.send(encoded_result)
        logger.debug('Server {} closes the connection with {}:{}'.format(self.get_short_uuid(), *addr))
        conn.close()

    def handle_client_request(self, op, kwargs):
        if op == 'try_lock':
            if self.lock_type == C.RWLOCK:
                # self.rwlock.write_acquire()
                # logger.debug('Server {} acquires write lock when handling client request {}'.format(
                #     self.get_short_uuid(), op))
                result = self.preempt_lock(**kwargs)
                # logger.debug('Server {} releases write lock after handling client request {}'.format(
                #     self.get_short_uuid(), op))
                # self.rwlock.write_release()
            else:
                # self.mutex.acquire()
                # logger.debug('Server {} acquires mutex lock when handling client request {}'.format(
                #     self.get_short_uuid(), op))
                result = self.preempt_lock(**kwargs)
                # logger.debug('Server {} releases mutex lock after handling client request {}'.format(
                #     self.get_short_uuid(), op))
                # self.mutex.release()
        elif op == 'try_unlock':
            if self.lock_type == C.RWLOCK:
                # self.rwlock.write_acquire()
                # logger.debug('Server {} acquires write lock when handling client request {}'.format(
                #     self.get_short_uuid(), op))
                result = self.release_lock(**kwargs)
                # logger.debug('Server {} releases write lock after handling client request {}'.format(
                #     self.get_short_uuid(), op))
                # self.rwlock.write_release()
            else:
                # self.mutex.acquire()
                # logger.debug('Server {} acquires mutex lock when handling client request {}'.format(
                #     self.get_short_uuid(), op))
                result = self.release_lock(**kwargs)
                # logger.debug('Server {} releases mutex lock after handling client request {}'.format(
                #     self.get_short_uuid(), op))
                # self.mutex.release()
        elif op == 'own_the_lock':
            if self.lock_type == C.RWLOCK:
                self.rwlock.read_acquire()
                logger.debug('Server {} acquires read lock when handling client request {}'.format(
                    self.get_short_uuid(), op))
                result = self.check_lock(**kwargs)
                logger.debug('Server {} acquires read lock when handling client request {}'.format(
                    self.get_short_uuid(), op))
                self.rwlock.read_release()
            else:
                result = self.check_lock(**kwargs)
        else:
            logger.error('Unsupported client request op {}'.format(op))
            result = None
        return result

    def handle_server_request(self, op, args):
        if op == 'request_to_update':
            if self.lock_type == C.RWLOCK:
                self.rwlock.write_acquire()
                logger.debug('Follower {} acquires write lock when handling leader request {}'.format(
                    self.get_short_uuid(), op))
                result = self.handle_update_request(args)
                logger.debug('Follower {} releases write lock after handling leader request {}'.format(
                    self.get_short_uuid(), op))
                self.rwlock.write_release()
            else:
                self.mutex.acquire()
                logger.debug('Follower {} acquires mutex lock when handling leader request {}'.format(
                    self.get_short_uuid(), op))
                result = self.handle_update_request(args)
                logger.debug('Follower {} releases mutex lock after handling leader request {}'.format(
                    self.get_short_uuid(), op))
                self.mutex.release()
        else:
            logger.error('Unsupported server request op {}'.format(op))
            result = None
        return result

    def check_lock(self, lock_key, client_id):
        logger.debug('Server {} performing operation "check_lock", lock_key="{}", client_id="{}"'.format(
            self.get_short_uuid(), lock_key, client_id))
        if lock_key in self.lock_map:
            return self.lock_map[lock_key] == client_id
        else:
            return False

    def preempt_lock(self, lock_key, client_id):
        logger.debug('Server {} performing operation "preempt_lock", lock_key="{}", client_id="{}"'.format(
            self.get_short_uuid(), lock_key, client_id))
        logger.debug('Follower {} requesting leader to preempt lock, lock_key="{}", client_id="{}"'.format(
            self.get_short_uuid(), lock_key, client_id))

        request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        request_socket.connect((self.leader.ip, self.leader.port))
        request_data = {'type': 'server', 'op': 'preempt_lock', 'args': {'lock_key': lock_key, 'client_id': client_id}}
        encoded_request_data = json.dumps(request_data).encode('utf-8')
        request_socket.send(encoded_request_data)
        received_data = json.loads(request_socket.recv(1024).decode())
        request_socket.close()

        logger.debug('Follower {} request preempt lock, lock_key="{}", client_id="{}", result:{}'.format(
            self.get_short_uuid(), lock_key, client_id, received_data))
        return received_data

    def release_lock(self, lock_key, client_id):
        logger.debug('Server {} performing operation "release_lock", lock_key="{}", client_id="{}"'.format(
            self.get_short_uuid(), lock_key, client_id))
        logger.debug('Follower {} requesting leader to release lock, lock_key="{}", client_id="{}"'.format(
            self.get_short_uuid(), lock_key, client_id))

        request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        request_socket.connect((self.leader.ip, self.leader.port))
        request_data = {'type': 'server', 'op': 'release_lock', 'args': {'lock_key': lock_key, 'client_id': client_id}}
        encoded_request_data = json.dumps(request_data).encode('utf-8')
        request_socket.send(encoded_request_data)
        received_data = json.loads(request_socket.recv(1024).decode())
        request_socket.close()

        logger.debug('Follower {} request release lock, lock_key="{}", client_id="{}", result:{}'.format(
            self.get_short_uuid(), lock_key, client_id, received_data))
        return received_data

    def handle_update_request(self, lock_map):
        logger.debug('Follower {} updating lock map...'.format(self.get_short_uuid()))
        self.update_lock_map(lock_map)
        # logger.debug('Follower {} update lock map finished!'.format(self.get_short_uuid()))
        return True
