import utils as F

import multiprocessing
import logging

logger = logging.getLogger('main' + '.' + __name__)

class Leader:

    def __init__(self, ip):
        self.ip = ip
        self.uuid = F.generate_uuid_by_ip(self.ip)
        self.lock_map = {}
        self.followers = []
        self.connections_to_followers = []
        self.connection_to_client = None

    def __str__(self):
        description = "Leader server: {}\n".format(self.uuid)
        description = "ip: {}\n".format(self.ip)
        description += "followers: {}\n".format([x.uuid for x in self.followers])
        description += "lock_map: {}\n".format(self.lock_map)
        return description

    def establish_connections_to_followers(self):
        for follower in self.followers:
            logger.info('Establishing connection between leader {}({}) and follower {}({})...'.format(
                self.uuid, self.ip, follower.uuid, follower.ip))
            conn1, conn2 = multiprocessing.Pipe()
            self.connections_to_followers.append(conn1)
            follower.connection_to_leader = conn2
            logger.info('Connection establishment completed!')

    def update_lock_map(self, lock_map):
        self.lock_map = lock_map

    def add_followers(self, followers):
        self.followers.extend(followers)

    def check_lock(self, lock_key, client_id):
        print('Server {}'.format(self.uuid))
        print('performing operation "check_lock", lock_key="{}", client_id="{}"'.format(lock_key, client_id))
        if lock_key in self.lock_map:
            return self.lock_map[lock_key] == client_id
        else:
            return False

    def preempt_lock(self, lock_key, client_id):
        logger.info('Server {}({})'.format(self.uuid, self.ip))
        print('performing operation "preempt_lock", lock_key="{}", client_id="{}"'.format(lock_key, client_id))
        if lock_key not in self.lock_map:
            self.lock_map[lock_key] = client_id
            self.request_to_update()
            return True
        else:
            return False

    def release_lock(self, lock_key, client_id):
        print('Server {}'.format(self.uuid))
        print('performing operation "release_lock", lock_key="{}", client_id="{}"'.format(lock_key, client_id))
        if self.check_lock(lock_key, client_id):
            del self.lock_map[lock_key]
            self.request_to_update()
            return True
        else:
            return False

    def request_to_update(self):
        print('Leader {} request to update followers...'.format(self.uuid))
        for follower in self.followers:
            answer = follower.handle_update_request(self.lock_map)
            if answer == False:
                print('Request to update follower {} failed!'.format(follower.uuid))
        print('Request to update all finished!')
        return True
