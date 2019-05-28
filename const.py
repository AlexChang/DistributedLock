# ip
LOCALHOST = '127.0.0.1'

# operation
OPERATION_MAPPING = {
    100: "try_lock",
    101: "try_unlock",
    102: "own_the_lock"
}

# lock
MUTEX = 1000
RWLOCK = 1001

LOCK_MAPPING = {
    'mutex': MUTEX,
    'rwlock': RWLOCK
}

# consensus
WEAK = 2000
STRONG = 2001

CONSENSUS_MAPPING = {
    'weak': WEAK,
    'strong': STRONG
}
