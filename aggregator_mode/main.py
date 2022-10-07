import sys, os, time, glob, copy, configparser, socket, ast, logging
sys.path.insert(1, '..')       
import utils

config = configparser.ConfigParser()
config.read('../config_4.ini')

group_id = sys.argv[1]

aggregator_ip = config[group_id]['AGGREGATOR_IP']
exchanger_ip = config[group_id]['EXCHANGER_IP']
trainer_ip = ast.literal_eval(config[group_id]['TRAINER_IP'])
num_communication_rounds = int(config['TRAINING']['NUM_COMMUNICATION_ROUNDS'])
hostname = socket.gethostname()
logging.basicConfig(filename="%s_log.txt"%hostname, level=logging.DEBUG, format="%(asctime)s - %(message)s")

logging.info("[START] RECEIVE INIT MODEL")
while not os.path.exists('exchanged_models/model_ep%d.h5'%(0)):
    time.sleep(5)
# os.system('cp exchanged_models/model_ep%d.h5 aggregated_models/%s_ep%d.h5'%(0,hostname,0))
logging.info("[COMPLETE] RECEIVE INIT MODEL")

logging.info("[START] BROADCAST INIT MODEL")
utils.broadcast_model(trainer_ip,19192,'exchanged_models/model_ep%d.h5'%(0), 'exchanged_models')
logging.info("[COMPLETE] BROADCAST INIT MODEL")

for e in range(num_communication_rounds):

    logging.info("[START] RECEIVE TRAINED MODEL IN EP%d"%e)
    while True:
        if len(glob.glob('trained_models/*_ep%d.h5'%(e))) == len(trainer_ip):
            break
    logging.info("[COMPLETE] RECEIVE TRAINED MODEL IN EP%d"%e)
    
    logging.info("[START] AGGREGATING TRAINED MODEL IN EP%d"%e)
    # arr = []
    # model = utils.model_init()
    # model.load_weights('exchanged_models/model_ep%d.h5'%(e))
    # arr.append(copy.deepcopy(model.get_weights()))
    # for p in glob.glob('trained_models/*_ep%d.h5'%(e)):
    #     model = utils.model_init()
    #     while not os.path.exists(p):
    #         time.sleep(5)
    #     model.load_weights(p)
    #     # while not os.path.exists(p):
    #     #     try:
    #     #         model.load_weights(p)
    #     #     except:
    #     #         pass
    #     arr.append(copy.deepcopy(model.get_weights()))
    # arr_avg = utils.aggregated(arr)
    # aggregated_model = utils.model_init()
    # aggregated_model.set_weights(arr_avg)


    arr = []
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
    arr.append('exchanged_models/model_ep%d.h5'%(e))
    for p in glob.glob('trained_models/*_ep%d.h5'%(e)):
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
    aggregated_model = utils.aggregated(arr)
    aggregated_model.save_weights('aggregated_models/%s_ep%d.h5'%(hostname,e+1))

    while not os.path.exists('aggregated_models/%s_ep%d.h5'%(hostname,e+1)):
            time.sleep(5)
    time.sleep(5)
    logging.info("[COMPLETE] AGGREGATING TRAINED MODEL IN EP%d"%e)

    logging.info("[START] TRANSFER TRAINED MODEL IN EP%d TO EXCHANGER NODE"%e)
    utils.send_model(exchanger_ip,19190,'aggregated_models/%s_ep%d.h5'%(hostname,e+1), 'aggregated_models')
    while not os.path.exists('exchanged_models/model_ep%d.h5'%(e+1)):
            time.sleep(5)
    time.sleep(5)
    logging.info("[COMPLETE] TRANSFER TRAINED MODEL IN EP%d TO EXCHANGER NODE"%e)

    logging.info("[START] BROADCAST EXCHANGED MODEL IN EP%d"%e)
    utils.broadcast_model(trainer_ip,19192,'exchanged_models/model_ep%d.h5'%(e+1), 'exchanged_models')
    logging.info("[COMPLETE] BROADCAST EXCHANGED MODEL IN EP%d"%e)