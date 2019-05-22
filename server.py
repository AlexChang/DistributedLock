import utils as F

class Server:

    def __init__(self, is_leader=False):
        self.uuid = F.generate_uuid()
        self.lock_map = {}
        self.is_leader = is_leader
        self.leader = None
        self.followers = []

    def __str__(self):
        if self.is_leader:
            description = "Leader server: {}\n".format(self.uuid)
            description += "followers: {}\n".format([x.uuid for x in self.followers])
        else:
            description = "Follower server: {}\n".format(self.uuid)
            description += "leader: {}\n".format(self.leader.uuid)
            description += "peers: {}\n".format([x.uuid for x in self.followers])
        description += "lock_map: {}\n".format(self.lock_map)
        return description

    def update_lock_map(self, lock_map):
        self.lock_map = lock_map

    def add_leader(self, leader):
        self.leader = leader

    def add_follower(self, follower):
        self.followers.append(follower)

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
        print('Server {}'.format(self.uuid))
        print('performing operation "preempt_lock", lock_key="{}", client_id="{}"'.format(lock_key, client_id))
        if self.is_leader:
            if lock_key not in self.lock_map:
                self.lock_map[lock_key] = client_id
                self.request_to_update()
                return True
            else:
                return False
        else:
            return self.leader.preempt_lock(lock_key, client_id)

    def release_lock(self, lock_key, client_id):
        print('Server {}'.format(self.uuid))
        print('performing operation "release_lock", lock_key="{}", client_id="{}"'.format(lock_key, client_id))
        if self.is_leader:
            if self.check_lock(lock_key, client_id):
                del self.lock_map[lock_key]
                self.request_to_update()
                return True
            else:
                return False
        else:
            return self.leader.release_lock(lock_key, client_id)

    def request_to_update(self):
        print('Leader {} request to update followers...'.format(self.uuid))
        for follower in self.followers:
            answer = follower.handle_update_request(self.lock_map)
            if answer == False:
                print('Request to update follower {} failed!'.format(follower.uuid))
        print('Request to update all finished!')
        return True

    def handle_update_request(self, lock_map):
        print('Follower {} updating...'.format(self.uuid))
        self.update_lock_map(lock_map)
        print('Follower updating finished!')
        return True