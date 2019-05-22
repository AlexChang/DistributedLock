import utils as F

import logging

logger = logging.getLogger('main' + '.' + __name__)

class Follower:

    def __init__(self, ip):
        self.ip = ip
        self.uuid = F.generate_uuid_by_ip(self.ip)
        self.lock_map = {}
        self.leader = None
        self.connection_to_master = None

    def __str__(self):
        description = "Follower server: {}\n".format(self.uuid)
        description = "ip: {}\n".format(self.ip)
        description += "leader: {}\n".format(self.leader.uuid)
        description += "lock_map: {}\n".format(self.lock_map)
        return description

    def update_lock_map(self, lock_map):
        self.lock_map = lock_map

    def add_leader(self, leader):
        self.leader = leader

    def check_lock(self, lock_key, client_id):
        print('Server {}'.format(self.uuid))
        print('performing operation "check_lock", lock_key="{}", client_id="{}"'.format(lock_key, client_id))
        if lock_key in self.lock_map:
            return self.lock_map[lock_key] == client_id
        else:
            return False

    def preempt_lock(self, lock_key, client_id):
        print('Server {}'.format(self.uuid))
        print('performing operation "preempt_lock", lock_key="{}", client_id="{}"'.format(lock_key, client_id))
        return self.leader.preempt_lock(lock_key, client_id)

    def release_lock(self, lock_key, client_id):
        print('Server {}'.format(self.uuid))
        print('performing operation "release_lock", lock_key="{}", client_id="{}"'.format(lock_key, client_id))
        return self.leader.release_lock(lock_key, client_id)

    def handle_update_request(self, lock_map):
        print('Follower {} updating...'.format(self.uuid))
        self.update_lock_map(lock_map)
        print('Follower updating finished!')
        return True
