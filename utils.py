import parameter as P

import uuid
import random
import os
import logging

logger = logging.getLogger('main' + '.' + __name__)


def generate_uuid():
    return str(uuid.uuid4())


def generate_uuid_by_ip(ip, namespace=uuid.NAMESPACE_OID):
    if namespace:
        return str(uuid.uuid5(namespace, ip))
    else:
        return str(uuid.uuid5(uuid.NAMESPACE_OID, ip))


def rand_item(my_list):
    """random item from my_list"""
    return random.choice(my_list)


def rand_int(my_range):
    """int in [my_range[0], my_range[1]]"""
    return random.randint(my_range[0], my_range[1])


def check_path_validity():
    logger.info("Checking path validity...")
    if not os.path.exists(P.log_path):
        logger.info("Directory {} does not exist, creating...".format(P.log_path))
        os.makedirs(P.log_path)
    logger.info("Check path validation process done!")
