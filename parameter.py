leader_num = 1
follower_num = 2
client_num = follower_num + leader_num
exp_num = 100

# ip
LOCALHOST = '127.0.0.1'
port_range = (8000, 10000)

# server
server_time_out = 3
server_max_listen = 10

# path
log_path = './log/'

MUTEX = 1000
RWLOCK = 1001

nameToLockType = {
    'mutex': MUTEX,
    'rwlock': RWLOCK
}

lockTypeToName = {
    MUTEX: 'mutex',
    RWLOCK: 'rwlock'
}

# lock
lock_type = RWLOCK

# client operations
lock_key_num = 1
lock_key_range = (100, 200)
client_operation_range = (100, 102)

OPERATION_MAPPING = {
    100: "try_lock",
    101: "try_unlock",
    102: "own_the_lock"
}