# Distributed Lock

## multi process

* client(request to server(random sleep)) * 3
* server(listen to client) * 3
* leader(listen to follower, request to follower(thread)) * 2
* follower(listen to leader, request to leader(thread)) * 2