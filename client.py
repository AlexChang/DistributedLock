import utils as F

import logging

logger = logging.getLogger('main' + '.' + __name__)

class Client:

    def __init__(self, ip):
        self.ip = ip
        self.uuid = F.generate_uuid_by_ip(self.ip)
        self.server = None

    def __str__(self):
        description = "Client: {}\nip: {}\nserver: {}\n".format(self.uuid, self.ip, self.server.uuid)
        return description

    def update_corresponding_server(self, server):
        self.server = server

    def try_lock(self, lock_key):
        print('Client: {}'.format(self.uuid))
        print('performing "try_lock" operation with lock_key = "{}"'.format(lock_key))
        result = self.server.preempt_lock(lock_key, self.uuid)
        print('client operation result: {}\n'.format(result))

    def try_unlock(self, lock_key):
        print('Client: {}'.format(self.uuid))
        print('performing "try_unlock" operation with lock_key = "{}"'.format(lock_key))
        result = self.server.release_lock(lock_key, self.uuid)
        print('client operation result: {}\n'.format(result))

    def own_the_lock(self, lock_key):
        print('Client: {}'.format(self.uuid))
        print('performing "own_the_lock" operation with lock_key = "{}"'.format(lock_key))
        result = self.server.check_lock(lock_key, self.uuid)
        print('client operation result: {}\n'.format(result))