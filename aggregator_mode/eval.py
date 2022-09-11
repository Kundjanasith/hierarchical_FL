import sys, os, time, glob, copy
sys.path.insert(1, '..')       
import utils

local_ip = ['10.10.100.34', '10.10.100.35', '10.10.100.36', '10.10.100.37', '10.10.100.38', '10.10.100.39', '10.10.100.40', '10.10.100.41', '10.10.100.42']
model = utils.model_init()
(X_train, Y_train), (X_test, Y_test) = utils.load_dataset()

NUM_ROUNDS = 10
file_out = open('log.txt','w')
file_out.write('ep,')
for ip in local_ip:
    file_out.write(ip+',')
file_out.write('global\n')

for e in range(NUM_ROUNDS):
    file_out.write('%d,'%e)
    # for ip in local_ip:
    #     model.load_weights('local_models/%s_ep%d.h5'%(ip,e))
    #     model.compile(optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])
    #     _, acc = model.evaluate(X_test, Y_test)
    #     file_out.write('%f,'%acc)
    model.load_weights('global_models/aggregated_model_ep%d.h5'%(e))
    model.compile(optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])
    _, acc = model.evaluate(X_test, Y_test)
    file_out.write('%f\n'%acc)
    
