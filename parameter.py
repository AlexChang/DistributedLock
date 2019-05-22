follower_num = 2
client_num = follower_num + 1
exp_num = 10

log_path = './log/'

# client operations
client_operation_range = (100, 102)

OPERATION_MAPPING = {
    100: "try_lock",
    101: "try_unlock",
    102: "own_the_lock"
}