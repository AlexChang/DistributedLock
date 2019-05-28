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
import multiprocessing
import threading
import socket
import json

def initArgParser():
    parser = argparse.ArgumentParser(description='Distributed Lock')
    parser.add_argument('--lp', type=str, default='./log/', help='log path')
    args = parser.parse_args()
    return args

def init_logger(algo='DistributedLock', time_suffix=''):
    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s.%(funcName)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler(P.log_path + algo + '_detail_' + time_suffix + '.log', mode='w')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.FileHandler(P.log_path + algo + '_' + time_suffix + '.log', mode='w')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger


def main():

    F.check_path_validity()

    time_suffix = time.strftime('%y%m%d_%H%M%S')
    logger = init_logger(time_suffix=time_suffix)

    # init servers
    ports = F.rand_items_in_range(P.leader_num + P.follower_num, P.port_range)
    servers = []
    for i in range(P.leader_num + P.follower_num):
        if i == 0:
            leader = Leader(ports[i])
            servers.append(leader)
            threading.Thread(target=leader.init_server).start()
        else:
            follower = Follower(ports[i])
            leader.add_follower(follower)
            follower.add_leader(leader)
            servers.append(follower)
            threading.Thread(target=follower.init_server).start()

    # init clients
    clients = []
    for i in range(P.client_num):
        client = Client()
        client.add_corresponding_server(servers[i])
        clients.append(client)

    # request
    lock_keys = F.rand_items_in_range(P.lock_key_num, P.lock_key_range)
    thread_list = []
    for i in range(P.exp_num):
        # print("Operation No.{}".format(i + 1))
        client = F.rand_item(clients)
        operation_code = F.rand_int(P.client_operation_range)
        operation_name = P.OPERATION_MAPPING[operation_code]
        func = getattr(client, operation_name)
        t = threading.Thread(target=func, args=(F.rand_item(lock_keys),))
        thread_list.append(t)
        t.start()

    # join request
    for t in thread_list:
        t.join()

    # close servers
    time.sleep(0.1)
    for s in servers:
        logger.info('Shutting down server {}'.format(s.get_short_uuid()))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((s.ip, s.port))
        send_data = {'type': 'close'}
        encoded_send_data = json.dumps(send_data).encode('utf-8')
        client_socket.send(encoded_send_data)
        client_socket.close()

    time.sleep(5)
    logger.info('All done!')


if __name__ == '__main__':
    main()