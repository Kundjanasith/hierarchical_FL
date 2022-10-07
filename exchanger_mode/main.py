import sys, os, time, glob, copy, configparser, socket, ast, logging
sys.path.insert(1, '..')       
import utils

config = configparser.ConfigParser()
config.read('../config_4.ini')

aggregator_ip = []
for group in ast.literal_eval(config['TRAINING']['GROUPS']):
    aggregator_ip.append(config[group]['AGGREGATOR_IP'])
num_communication_rounds = int(config['TRAINING']['NUM_COMMUNICATION_ROUNDS'])
hostname = socket.gethostname()
logging.basicConfig(filename="%s_log.txt"%hostname, level=logging.DEBUG, format="%(asctime)s - %(message)s")

logging.info("[START] INIT MODEL")
init_model = utils.model_init()
init_model.save_weights('exchanged_models/model_ep%d.h5'%(0))
while not os.path.exists('exchanged_models/model_ep%d.h5'%(0)):
    time.sleep(10)
logging.info("[COMPLETE] INIT MODEL")

logging.info("[START] BROADCAST INIT MODEL")
utils.broadcast_model(aggregator_ip,19191,'exchanged_models/model_ep%d.h5'%(0), 'exchanged_models')
logging.info("[COMPLETE] BROADCAST INIT MODEL")

for e in range(1,num_communication_rounds):

    logging.info("[START] RECEIVE AGGREGATED MODEL IN EP%d"%e)
    while True:
        if len(glob.glob('aggregated_models/*_ep%d.h5'%(e))) == len(aggregator_ip):
            break
    logging.info("[COMPLETE] RECEIVE AGGREGATED MODEL IN EP%d"%e)

    logging.info("[START] AGGREGATING AGGREGATED MODEL IN EP%d"%e)
    # arr = []
    # for p in glob.glob('aggregated_models/*_ep%d.h5'%(e)):
    #     model = utils.model_init()
    #     while not os.path.exists(p):
    #         print('waiting',p)
    #         model.load_weights(p)
    #     # while not os.path.exists(p):
    #     #     try:
    #     #         model.load_weights(p)
    #     #     except:
    #     #         pass
    #     arr.append(copy.deepcopy(model.get_weights()))
    # arr_avg = utils.aggregated(arr)
    # exchanged_model = utils.model_init()
    # exchanged_model.set_weights(arr_avg)

    arr = []
    while True:
        print('aa')
        try:
            print('bb')
            model = utils.model_init()
            model.load_weights('exchanged_models/model_ep%d.h5'%(e-1))
            break
        except:
            print('cc')
            pass
    arr.append('exchanged_models/model_ep%d.h5'%(e-1))
    for p in glob.glob('aggregated_models/*_ep%d.h5'%(e)):
        # while not os.path.exists(p):
        #     time.sleep(5)
        while True:
            print('a',p)
            try:
                print('b',p)
                model = utils.model_init()
                model.load_weights(p)
                break
            except:
                print('c',p)
                pass
        arr.append(p)
    exchanged_model = utils.aggregated(arr)
    exchanged_model.save_weights('exchanged_models/model_ep%d.h5'%(e))
    logging.info("[COMPLETE] AGGREGATING AGGREGATED MODEL IN EP%d"%e)

    logging.info("[START] BROADCAST EXCHANGED MODEL IN EP%d"%e)
    utils.broadcast_model(aggregator_ip,19191,'exchanged_models/model_ep%d.h5'%(e), 'exchanged_models')
    logging.info("[COMPLETE] BROADCAST EXCHANGED MODEL IN EP%d"%e)




        
