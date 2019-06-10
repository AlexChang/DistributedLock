import utils as F
import parameter as P
import const as C

from client import Client
from leader import Leader
from follower import Follower

import sys
import argparse
import logging
import time
import json
import socket
import threading


def init_arg_parser():
    parser = argparse.ArgumentParser(description='Distributed Lock')
    parser.add_argument('--log_path', type=str, default='./log/', help='path to output log')
    parser.add_argument('--op_num', type=int, default=100, help='number of operations')
    parser.add_argument('--lock_type', type=str, default='rwlock', help='lock type(rwlock or mutex)')
    parser.add_argument('--consensus_type', type=str, default='strong', help='consensus_type(strong or weak)')
    parser.add_argument('--follower_num', type=int, default=3, help='number of followers')
    parser.add_argument('--lock_key_num', type=int, default=5, help='number of keys used in distributed lock(1~100)')
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
    # init
    args = init_arg_parser()
    P.log_path = args.log_path
    P.op_num = args.op_num
    P.lock_type = C.LOCK_MAPPING[args.lock_type]
    P.consensus_type = C.CONSENSUS_MAPPING[args.consensus_type]
    P.follower_num = args.follower_num
    P.lock_key_num = args.lock_key_num
    F.check_path_validity()
    time_suffix = time.strftime('%y%m%d_%H%M%S')
    logger = init_logger(time_suffix=time_suffix)
    F.save_parameter(time_suffix=time_suffix)

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
    time.sleep(0.1)
    clients = []
    for i in range(P.client_num):
        client = Client()
        client.add_corresponding_server(servers[i])
        clients.append(client)

    # client requests
    lock_keys = F.rand_items_in_range(P.lock_key_num, P.lock_key_range)
    thread_list = []
    for i in range(P.op_num):
        logger.info("Operation No.{}".format(i + 1))
        client = F.rand_item(clients)
        operation_code = F.rand_int(P.client_operation_range)
        operation_name = C.OPERATION_MAPPING[operation_code]
        func = getattr(client, operation_name)
        t = threading.Thread(target=func, args=(str(F.rand_item(lock_keys)),))
        thread_list.append(t)
        t.start()
        time.sleep(0.015)

    # join client requests
    for t in thread_list:
        t.join()

    # shut down servers
    time.sleep(0.1)
    for s in servers:
        logger.info('Shutting down server {}'.format(s.get_short_uuid()))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((s.ip, s.port))
        send_data = {'type': 'close'}
        encoded_send_data = json.dumps(send_data).encode('utf-8')
        client_socket.send(encoded_send_data)
        client_socket.close()

    # finish
    time.sleep(5)
    logger.info('All done!')


if __name__ == '__main__':
    main()
