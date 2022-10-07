import sys, os, time, configparser, socket, logging
sys.path.insert(1, '..')       
import utils

config = configparser.ConfigParser()
config.read('../config_4.ini')

group_id = sys.argv[1]

aggregator_ip = config[group_id]['AGGREGATOR_IP']
num_communication_rounds = int(config['TRAINING']['NUM_COMMUNICATION_ROUNDS'])
num_samples = int(config['TRAINING']['NUM_SAMPLES'])
local_batch_size = int(config['TRAINING']['LOCAL_BATCH_SIZE'])
local_epochs = int(config['TRAINING']['LOCAL_EPOCHS'])
hostname = socket.gethostname()
logging.basicConfig(filename="%s_log.txt"%hostname, level=logging.DEBUG, format="%(asctime)s - %(message)s")

for e in range(num_communication_rounds):

    logging.info("[START] RECEIVE EXCHANGED MODEL IN EP%d"%e)
    utils.receive_model('0.0.0.0',19192)
    logging.info("[COMPLETE] RECEIVE EXCHANGED MODEL IN EP%d"%e)

    logging.info("[START] TRAIN LOCAL MODEL IN EP%d"%e)
    model = utils.model_init()
    while not os.path.exists('exchanged_models/model_ep%d.h5'%(e)):
        time.sleep(5)
    # model.load_weights('exchanged_models/model_ep%d.h5'%(e))
    while True:
        print('aa')
        try:
            print('bb')
            model = utils.model_init()
            model.load_weights('exchanged_models/model_ep%d.h5'%(e))
            break
        except:
            print('cc')
            pass
    # while not os.path.exists('exchanged_models/model_ep%d.h5'%(e)):
    #     try:
    #         model.load_weights('exchanged_models/model_ep%d.h5'%(e))
    #     except:
    #         pass
    x_train, y_train = utils.sampling_data(num_samples)
    model.compile(optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(x_train, y_train,epochs=local_epochs,batch_size=local_batch_size,verbose=1,validation_split=0.2)
    model.save_weights('trained_models/%s_ep%d.h5'%(hostname,e))
    logging.info("[COMPLETE] TRAIN LOCAL MODEL IN EP%d"%e)

    logging.info("[START] SEND TRAINED MODEL IN EP%d"%e)
    utils.send_model(aggregator_ip, 19191,'trained_models/%s_ep%d.h5'%(hostname,e), 'trained_models')
    logging.info("[COMPLETE] SEND TRAINED MODEL IN EP%d"%e)

