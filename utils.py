from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet import MobileNet
from tensorflow.keras.layers import Input, Dense, BatchNormalization, Flatten
from tensorflow.keras import Model
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.backend import clear_session
import random
import numpy as np
import socket, os, time
from threading import Thread
from socketserver import ThreadingMixIn
import asyncio, logging
logging.getLogger('tensorflow').disabled = True


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
            f.close()
        time.sleep(1)

def send_model(tcp_ip, tcp_port, file_path, to_path):
    TCP_IP = tcp_ip
    TCP_PORT = tcp_port
    BUFFER_SIZE = 1024
    SEPARATOR = "<SEPARATOR>"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('XXXX',TCP_IP, TCP_PORT)
    s.connect((TCP_IP, TCP_PORT))
    s.send(bytes(f"{file_path.split('/')[1]}{SEPARATOR}{to_path}",'UTF-8'))
    time.sleep(10)
    with open(file_path, 'rb') as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            while True:
                try:
                    s.sendall(bytes_read)
                    print('SEND COMPLETE')
                    break
                except Exception as e:
                    print(e)
                    pass
        f.close()
    time.sleep(1)
    s.close()
    return 'complete'

def broadcast_model(tcp_ip_list, tcp_port, file_path, to_path):
    for ip in tcp_ip_list:
        # os.system('cp %s %s'%(file_path,file_path+ip))
        time.sleep(10)
        print('start transfer %s to %s'%(file_path,ip))
        res = send_model(ip, tcp_port, file_path, to_path)
        # print(res)
        # os.system('rm -rf %s'%(file_path+ip))
        time.sleep(10)
        print('end transfer %s to %s'%(file_path,ip))
    return 'complete'

def receive_model(tcp_ip, tcp_port):
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
        print(received)
        received = received.decode('UTF-8')
        filename, file_path = received.split(SEPARATOR)


        # filename, file_path = received.split(bytes(SEPARATOR,'UTF-8'))
        # print(filename, file_path)
        # filename = filename.decode('UTF-8')
        # file_path = file_path.decode('UTF-8')
        print('Got connection from ', (ip,port,file_path,filename))
        newthread = ClientThread(tcp_ip,tcp_port,conn,file_path+'/'+filename,BUFFER_SIZE)
        newthread.start()
        threads.append(newthread)
        time.sleep(10)
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

def sampling_data(num_samples):
    (x_train, y_train), (x_test, y_test) = load_dataset()
    print(len(x_train))
    num_of_each_dataset = num_samples
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
    # return MobileNetV2((32, 32, 3), classes=10, weights=None)

# def aggregated(server_weight):
#     avg_weight = np.array(server_weight[0])
#     if len(server_weight) > 1:
#         for i in range(1, len(server_weight)):
#             avg_weight += server_weight[i]
#     avg_weight = avg_weight / len(server_weight)
#     return avg_weight

def getLayerIndexByName(model, layername):
    for idx, layer in enumerate(model.layers):
        if layer.name == layername:
            return idx

def aggregated(model_path):
    global_model = model_init()
    global_model.load_weights(model_path[0])
    model_dict = {}
    count = 0
    for l in global_model.layers:
        l_idx = getLayerIndexByName(global_model, l.name)
        for w_idx in range(len(global_model.get_layer(index=l_idx).get_weights())):
            w = global_model.get_layer(index=l_idx).get_weights()[w_idx]
            model_dict[count] = []
            model_dict[count].append(w)
            count = count + 1
    clear_session()
    for p in model_path[1:]:
        count = 0
        client_model = model_init()
        print(p)
        client_model.load_weights(p)
        for l in client_model.layers:
            l_idx = getLayerIndexByName(client_model, l.name)
            for w_idx in range(len(client_model.get_layer(index=l_idx).get_weights())):
                w = client_model.get_layer(index=l_idx).get_weights()[w_idx]
                model_dict[count].append(w)
                count = count + 1
    clear_session()
    aggregated_model = model_init()
    count = 0
    for l in aggregated_model.layers:
        l_idx = getLayerIndexByName(aggregated_model, l.name)
        w_arr = []
        for w_idx in range(len(aggregated_model.get_layer(index=l_idx).get_weights())):
            w = aggregated_model.get_layer(index=l_idx).get_weights()[w_idx]
            w_avg = np.nanmean(np.array(model_dict[count]),axis=0)
            count = count + 1
            w_arr.append(w_avg)
        aggregated_model.get_layer(index=l_idx).set_weights(w_arr)
    return aggregated_model