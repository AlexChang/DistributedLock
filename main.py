import utils as F
import parameter as P

from client import Client
from server import Server
from leader import Leader
from follower import Follower

from faker import Faker

def main():

    fake = Faker()
    fake.seed(1234)

    # init servers
    leader = Leader(fake.ipv4())
    followers = [Follower(fake.ipv4()) for x in range(P.follower_num)]
    servers = [leader]
    servers.extend(followers)

    # config servers
    leader.add_followers(followers)
    for follower in followers:
        follower.add_leader(leader)

    # init clients
    clients = [Client(fake.ipv4()) for x in range(P.client_num)]

    # config client
    for idx, client in enumerate(clients):
        client.update_corresponding_server(servers[idx])

    for i in range(P.exp_num):
        print("Operation No.{}".format(i + 1))
        client = F.rand_item(clients)
        operation_code = F.rand_int(P.client_operation_range)
        operation_name = P.OPERATION_MAPPING[operation_code]
        func = getattr(client, operation_name)
        func(*('123', ))

    # status check
    for server in servers:
        print(server)
    for client in clients:
        print(client)


if __name__ == '__main__':
    main()