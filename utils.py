import parameter as P

import uuid
import random
import os
import logging
import json

logger = logging.getLogger('main' + '.' + __name__)
# random.seed(1)


def generate_uuid():
    return str(uuid.UUID(int=random.getrandbits(128)))


def generate_uuid_by_addr(addr, namespace=uuid.NAMESPACE_OID):
    if namespace:
        return str(uuid.uuid5(namespace, addr))
    else:
        return str(uuid.uuid5(uuid.NAMESPACE_OID, addr))


def rand_int(my_range):
    """int in [my_range[0], my_range[1]]"""
    return random.randint(my_range[0], my_range[1])


def rand_item(my_list):
    """random item from my_list"""
    return random.choice(my_list)


def rand_items_in_range(num, my_range):
    """generate num items in [my_range[0], my_range[1]]"""
    items = []
    while len(items) != num:
        item = rand_int(my_range)
        if item not in items:
            items.append(item)
    return items


def check_path_validity():
    logger.info("Checking path validity...")
    if not os.path.exists(P.log_path):
        logger.info("Directory {} does not exist, creating...".format(P.log_path))
        os.makedirs(P.log_path)
    logger.info("Check path validation process done!")


def save_parameter(filename='parameter', time_suffix=''):
    d = dict((name, getattr(P, name)) for name in dir(P) if not name.startswith('__'))
    del d['C']
    file_full_name = P.log_path + filename + '_' + time_suffix + '.json'
    logger.debug("Parameter: {}".format(d))
    logger.info("Saving parameter to file '{}'...".format(file_full_name))
    json.dump(d, open(file_full_name, 'w'))
    logger.info("Parameter saving process done!")