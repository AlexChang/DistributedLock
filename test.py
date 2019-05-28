import utils as F
import parameter as P
import multiprocessing
import socket
import threading
import time

class Master:
    def __init__(self):
        self.uuid = F.generate_uuid()
        self.slaves = []
        self.connection_to_slaves = []
        self.lock = {'123': 'abc'}

    def __str__(self):
        description = "Master: {}\n".format(self.uuid)
        return description

    def op(self, slave_id, msg):
        p2 = multiprocessing.Process(target=self.slaves[0].op, args=('Hello World!',))
        p2.start()
        connection = self.connection_to_slaves[slave_id]
        connection.send(self.lock)
        print(connection.recv())

class Slave:
    def __init__(self):
        self.uuid = F.generate_uuid()
        self.master = None
        self.connection_to_master = None

    def __str__(self):
        description = "Slave: {}\n".format(self.uuid)
        return description

    def op(self, msg):
        print(self.connection_to_master.recv())
        self.connection_to_master.send(msg)

def f(a, b):
    print(__name__)
    print(a)
    print(b)

class Test:

    mutex = threading.Lock()

    def __init__(self):
        self.l = []
        # self.mutex = threading.Lock()

    def f(self):
        # mutex = threading.Lock()
        for i in range(20):
            t = threading.Thread(target=self.g, args=(i, ))
            t.start()

    def g(self, n):
        time.sleep(1)
        self.mutex.acquire()
        self.l.append(n*n)
        print(self.l)
        self.mutex.release()


def main():
    # m = Master()
    # s_list = [Slave() for i in range(2)]
    # m.slaves.extend(s_list)
    # for s in s_list:
    #     s.master = m
    #
    # for s in m.slaves:
    #     conn1, conn2 = multiprocessing.Pipe()
    #     m.connection_to_slaves.append(conn1)
    #     s.connection_to_master = conn2
    #
    # p1 = multiprocessing.Process(target=m.op, args=(0, 'Hello'))
    #
    # p1.start()
    #
    # print(m)
    # for s in s_list:
    #     print(s)

    t = Test()
    multiprocessing.Process(target=t.f).start()
    # t.f()

    dict = {'a': 123, 'b': 456}
    f(**{'a': 123, 'b': 456})

    print(F.generate_uuid()[:8])

    print(vars(P))

    return

if __name__ == '__main__':
    main()