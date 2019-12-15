import numpy as np
import matplotlib.pyplot as plt
import queue

'''
Declaration of class Client:
    client_index: the index of client
    status: 
        WAITING: arrived but not served yet, waiting in queue
        LEFT: if the max queue length is limited and current queue is full, the client leaves immediately. Only available when limited_queue=True
        SERVING: under service
        FINISH: the service is done and the client leaves.
    server_index: the index of server during serving. 0 represents unserved
    waiting_time: the waiting time from arriving to being served
    staying_time: the total time including waiting and being served

Declaration of class Server:
    server_index: the index of server
    serving_time: when a new client comes, a new Exponential-distributed serving time is produced. 
    status: 
        IDLE: the server has just finished serving
        BUSY: the server is busy

Declaration of class Queuing:
    clients: an array of clients
    client_num: # of clients
    servers: an array of servers
    server_num: # of servers
    limited_queue: true if the queue has finite capability
    max_queue_len: maximum queue length
    timer: the current time. Initialized with 0 at the beginning
'''

UNDEF = -1
WAITING = 0
LEFT = 1
SERVING = 2
FINISH = 3
IDLE = 4
BUSY = 5


class ClientSim:
    client_index = -1
    status = UNDEF
    server_index = -1
    waiting_timestamp = -1
    serving_timestamp = -1
    leaving_timestamp = -1

    def __init__(self, client_index, status, waiting_timestamp):
        self.client_index = client_index
        self.status = status
        self.waiting_timestamp = waiting_timestamp
        pass
    
    def waiting_time(self):
        return self.serving_timestamp - self.waiting_timestamp

    def serving_time(self):
        return self.leaving_timestamp - self.serving_timestamp

    def staying_time(self):
        return self.leaving_timestamp - self.waiting_timestamp

    
class ServerSim:
    server_index = -1
    status = UNDEF
    serving_rate = 0
    serving_time = 0
    serving_time_elapsed = 0
    current_client = None

    def __init__(self, server_index, status, serving_rate):
        self.server_index = server_index
        self.status = status
        self.serving_rate = serving_rate
        pass

    def update_status(self, current_time):
        if self.serving_time_elapsed == self.serving_time and self.status == BUSY:
            self.current_client.leaving_timestamp = current_time
            client_index = self.current_client.client_index
            waiting_time = self.current_client.waiting_time()
            serving_time = self.current_client.serving_time()
            staying_time = self.current_client.staying_time()
            self.status = IDLE
            self.serving_time = 0
            self.serving_time_elapsed = 0
            self.current_client = None
            return client_index, waiting_time, serving_time, staying_time
        else:
            if self.status == BUSY:
                self.serving_time_elapsed = self.serving_time_elapsed + 1
        return -1, -1, -1, -1

    def create_client(self, current_time, new_client):
        self.serving_time = int(np.random.exponential(self.serving_rate))
        while self.serving_time == 0:
            self.serving_time = int(np.random.exponential(self.serving_rate))
        self.status = BUSY
        self.current_client = new_client
        self.current_client.serving_timestamp = current_time
        pass
    pass


class QueueSim:
    waiting_queue = queue.Queue()
    client_index = 0
    arriving_rate = -1
    serving_rate = -1
    server_num = -1
    max_queue_len = 0
    servers = []
    finish_list = []
    queue_len_list = []
    lost_list = []

    def __init__(self, arriving_rate, serving_rate, server_num, max_queue_len=0):
        self.arriving_rate = arriving_rate
        self.serving_rate = serving_rate
        self.server_num = server_num
        self.max_queue_len = max_queue_len
        for i in range(server_num):
            new_server = ServerSim(i, IDLE, self.serving_rate)
            self.servers.append(new_server)
        pass

    def simulate(self, duration=100):
        for t in range(duration):
            # Check if current service is end
            for srv in self.servers:
                index, waiting_time, serving_time, staying_time = srv.update_status(t)
                if not (index == -1 and waiting_time == -1 and serving_time == -1 and staying_time == -1):
                    self.finish_list.append([index, waiting_time, serving_time, staying_time])

            # New clients come
            arriving_client_num = np.random.poisson(self.arriving_rate)
            if arriving_client_num:
                for i in range(arriving_client_num):
                    new_client = ClientSim(self.client_index, WAITING, t)
                    new_client.waiting_timestamp = t
                    self.client_index = self.client_index + 1
                    if self.waiting_queue.qsize() < self.max_queue_len or self.max_queue_len == 0:
                        self.waiting_queue.put(new_client)
                    else:
                        self.lost_list.append([t, new_client.client_index])

            # Arrange clients to idle servers
            for srv in self.servers:
                if srv.status == IDLE:
                    if self.waiting_queue.qsize():
                        srv.create_client(t, self.waiting_queue.get())

            self.queue_len_list.append([t, self.waiting_queue.qsize()])

        return self.finish_list, self.queue_len_list, self.lost_list

    def show_clients(self):
        if self.finish_list:
            for fl in self.finish_list:
                print("ClientIndex:{} Waiting:{} Serving:{} Staying:{}".format(
                    fl[0], fl[1], fl[2], fl[3]))

    def show_queue(self):
        if self.queue_len_list:
            for qll in self.queue_len_list:
                print("Time: {} QueueLength: {}".format(qll[0], qll[1]))

    def show_lost(self):
        if self.lost_list:
            for ll in self.lost_list:
                print("Time:{} LostClientIndex:{}".format(ll[0], ll[1]))

    def mean_queue_len(self):
        if self.queue_len_list:
            queue_len = [x[1] for x in self.queue_len_list]
            return sum(queue_len) / len(queue_len)
        else:
            return -1

    def mean_time(self):
        if self.finish_list:
            wt_list = [x[1] for x in self.finish_list]
            srv_list = [x[2] for x in self.finish_list]
            st_list = [x[3] for x in self.finish_list]
            return sum(wt_list) / len(wt_list), sum(srv_list) / len(srv_list), sum(st_list) / len(st_list)
        else:
            return -1, -1, -1


if __name__ == "__main__":
    queue_sim = QueueSim(0.01, 60, 1)
    (res_finish, res_queue_len, res_lost_list) = queue_sim.simulate(7200)
    mean_queue_length = queue_sim.mean_queue_len()
    mean_waiting_time, mean_serving_time, mean_staying_time = queue_sim.mean_time()
    print("------------------------Statistics------------------------")
    print(" MeanQueueLength:{} \n MeanWaitingTime:{} \n MeanServingTime:{} \n MeanStayingTime:{}".format(
        mean_queue_length, mean_waiting_time, mean_serving_time, mean_staying_time
    ))
