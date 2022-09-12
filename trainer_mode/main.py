import sys, os, time, configparser, socket
sys.path.insert(1, '..')       
import utils

config = configparser.ConfigParser()
config.read('../config.ini')

group_id = sys.argv[1]

aggregator_ip = config[group_id]['AGGREGATOR_IP']
num_communication_rounds = int(config['TRAINING']['NUM_COMMUNICATION_ROUNDS'])
num_samples = int(config['TRAINING']['NUM_SAMPLES'])
local_batch_size = int(config['TRAINING']['LOCAL_BATCH_SIZE'])
local_epochs = int(config['TRAINING']['LOCAL_EPOCHS'])
hostname = socket.gethostname()

for e in range(num_communication_rounds):
    utils.receive_model('0.0.0.0',19192)
    model = utils.model_init()
    while not os.path.exists('exchanged_models/model_ep%d.h5'%(e)):
        try:
            model.load_weights('exchanged_models/model_ep%d.h5'%(e))
        except:
            pass
    x_train, y_train = utils.sampling_data(num_samples)
    model.compile(optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(x_train, y_train,epochs=local_epochs,batch_size=local_batch_size,verbose=1,validation_split=0.2)
    model.save_weights('trained_models/%s_ep%d.h5'%(hostname,e))
    utils.send_model(aggregator_ip, 19191,'trained_models/%s_ep%d.h5'%(hostname,e), 'trained_models')

