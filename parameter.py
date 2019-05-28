import const as C

##########
# global #
##########
# path
log_path = './log/'
# op number
op_num = 100
# lock type
lock_type = C.RWLOCK
# consensus type
consensus_type = C.STRONG

##########
# server #
##########
# number
leader_num = 1
follower_num = 3
# port
port_range = (8000, 10000)
# listen & time_out
server_max_listen = 10
server_time_out = 3

##########
# client #
##########
# number
client_num = follower_num + leader_num
# client operations
lock_key_num = 5
lock_key_range = (100, 200)
client_operation_range = (100, 102)
