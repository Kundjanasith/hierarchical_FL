from tensorflow.keras.applications.mobilenet import MobileNet
from tensorflow.keras.layers import Input, Dense, BatchNormalization, Flatten
from tensorflow.keras import Model
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import SGD
import random
import numpy as np
import socket, os, time
from threading import Thread
from socketserver import ThreadingMixIn
import asyncio


class ClientThread(Thread):
    def __init__(self,ip,port,sock,file_path,buffer):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        self.file_path = file_path
        self.buffer = buffer
        print(" New thread started for "+ip+":"+str(port))
    def run(self):
        with open(self.file_path, "wb") as f:
            while True:
                bytes_read = self.sock.recv(self.buffer)
                if not bytes_read:    
                    break
                f.write(bytes_read)

def send_model(tcp_ip, tcp_port, file_path):
    TCP_IP = tcp_ip
    TCP_PORT = tcp_port
    BUFFER_SIZE = 1024
    SEPARATOR = "<SEPARATOR>"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(bytes(f"{file_path.split('/')[1]}{SEPARATOR}",'UTF-8'))
    with open(file_path, 'rb') as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            s.sendall(bytes_read)
    s.close()
    return 'complete'

def broadcast_model(tcp_ip_list, tcp_port, file_path):
    for ip in tcp_ip_list:
        send_model(ip, tcp_port, file_path)
    return 'complete'

def receive_model(tcp_ip, tcp_port, file_path):
    TCP_IP = tcp_ip
    TCP_PORT = tcp_port
    BUFFER_SIZE = 1024
    SEPARATOR = "<SEPARATOR>"
    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpsock.bind((TCP_IP, TCP_PORT))
    threads = []
    while True:
        tcpsock.listen(5)
        print("Waiting for incoming connections...")
        (conn, (ip,port)) = tcpsock.accept()
        # received = conn.recv(BUFFER_SIZE).decode()
        received = conn.recv(BUFFER_SIZE)
        filename, _ = received.split(bytes(SEPARATOR,'UTF-8'))
        print('Got connection from ', (ip,port))
        newthread = ClientThread(tcp_ip,tcp_port,conn,file_path+'/'+filename,BUFFER_SIZE)
        newthread.start()
        threads.append(newthread)
        if os.path.exists(file_path+'/'+filename):
            break
    for t in threads:
        t.join()
    return 'complete'


def load_dataset():
    (X_train, Y_train), (X_test, Y_test) = cifar10.load_data()
    X_train = X_train.astype('float32')
    X_test = X_test.astype('float32')
    X_train = X_train / 255.0
    X_test = X_test / 255.0
    Y_train = to_categorical(Y_train)
    Y_test = to_categorical(Y_test)
    return (X_train, Y_train), (X_test, Y_test)

def sampling_data():
    (x_train, y_train), (x_test, y_test) = load_dataset()
    print(len(x_train))
    num_of_each_dataset = 1000
    print(num_of_each_dataset)
    split_data_index = []
    while len(split_data_index) < num_of_each_dataset:
        item = random.choice(range(x_train.shape[0]))
        if item not in split_data_index:
            split_data_index.append(item)
    new_x_train = np.asarray([x_train[k] for k in split_data_index])
    new_y_train = np.asarray([y_train[k] for k in split_data_index])
    return new_x_train, new_y_train

def model_init():
    model = MobileNet(include_top=False,input_tensor=Input(shape=(32,32,3)))
    x = model.output
    x = Flatten()(x)
    x = Dense(512,activation='relu')(x)
    x = BatchNormalization()(x)
    x = Dense(10,activation='softmax')(x)
    model = Model(model.input,x)
    return model

def aggregated(server_weight):
    avg_weight = np.array(server_weight[0])
    if len(server_weight) > 1:
        for i in range(1, len(server_weight)):
            avg_weight += server_weight[i]
    avg_weight = avg_weight / len(server_weight)
    return avg_weight