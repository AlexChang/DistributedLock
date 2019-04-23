import uuid
import random

def generate_uuid():
    return str(uuid.uuid4())

def rand_item(list):
    """random item from list"""
    return random.choice(list)

def rand_int(range):
    """int in [range[0], range[1]]"""
    return random.randint(range[0], range[1])