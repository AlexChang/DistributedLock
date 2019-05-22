import utils as F
import parameter as P

from client import Client
from server import Server
from leader import Leader
from follower import Follower

import sys
import argparse
import logging
import time
from faker import Faker

def initArgParser():
    parser = argparse.ArgumentParser(description='Distributed Lock')
    parser.add_argument('--lp', type=str, default='./log/', help='log path')
    args = parser.parse_args()
    return args

def init_logger(time_suffix=''):
    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s.%(funcName)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler(P.log_path + '_detail_' + time_suffix + '.log', mode='w')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.FileHandler(P.log_path + '_' + time_suffix + '.log', mode='w')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger


def main():

    # init
    fake = Faker()
    fake.seed(1234)

    F.check_path_validity()

    time_suffix = time.strftime('_%y%m%d_%H%M%S')
    logger = init_logger(time_suffix)

    # init servers
    leader = Leader(fake.ipv4())
    followers = [Follower(fake.ipv4()) for x in range(P.follower_num)]
    servers = [leader]
    servers.extend(followers)

    # config servers
    leader.add_followers(followers)
    for follower in followers:
        follower.add_leader(leader)
    leader.establish_connections_to_followers()

    # init clients
    clients = [Client(fake.ipv4()) for x in range(P.client_num)]

    # config client
    for idx, client in enumerate(clients):
        server = servers[idx]
        client.add_corresponding_server(servers[idx])
        logger.info('Assign server {}({}) to client {}({})'.format(server.uuid, server.ip, client.uuid, client.ip))
        client.establish_connections_to_server()

    # request
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