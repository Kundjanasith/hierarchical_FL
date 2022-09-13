import sys, os, time, glob, copy, configparser, ast
sys.path.insert(1, '..')       
import utils

config = configparser.ConfigParser()
config.read('../config.ini')

group_id = sys.argv[1]

trainer_ip = ast.literal_eval(config[group_id]['TRAINER_IP'])
num_communication_rounds = int(config['TRAINING']['NUM_COMMUNICATION_ROUNDS'])

model = utils.model_init()
(X_train, Y_train), (X_test, Y_test) = utils.load_dataset()

file_out = open('log.txt','w')
file_out.write('ep,')
for ip in trainer_ip:
    file_out.write(ip+',')
file_out.write('global\n')

for e in range(1,101):
    file_out.write('%d,'%e)
    list_trained_models = glob.glob('trained_models/*_ep%d.h5'%e)
    list_trained_models.sort()
    list_aggregated_models = glob.glob('aggregated_models/*_ep%d.h5'%e)
    list_aggregated_models.sort()
    print(list_aggregated_models)
    # for p in list_trained_models:
    #    model.load_weights(p)
    #    model.compile(optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])
    #    _, acc = model.evaluate(X_test, Y_test)
    #    file_out.write('%f,'%acc)
    model.load_weights(list_aggregated_models[0])
    model.compile(optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])
    _, acc = model.evaluate(X_test, Y_test, verbose=2)
    file_out.write('%f\n'%acc)
    
