import sys, os, time, glob, copy, configparser, socket, ast
sys.path.insert(1, '..')       
import utils

config = configparser.ConfigParser()
config.read('../config.ini')

group_id = sys.argv[1]

aggregator_ip = config[group_id]['AGGREGATOR_IP']
trainer_ip = ast.literal_eval(config[group_id]['TRAINER_IP'])
num_communication_rounds = int(config['TRAINING']['NUM_COMMUNICATION_ROUNDS'])
hostname = socket.gethostname()

init_model = utils.model_init()
init_model.save_weights('aggregated_models/%s_ep%d.h5'%(hostname,0))
while not os.path.exists('aggregated_models/%s_ep%d.h5'%(hostname,0)):
    time.sleep(10)

utils.broadcast_model(trainer_ip,19192,'aggregated_models/%s_ep%d.h5'%(hostname,0), 'exchanged_models')

for e in range(num_communication_rounds):
    while True:
        if len(glob.glob('trained_models/*_ep%d.h5'%(e))) == len(trainer_ip):
            break
    arr = []
    model = utils.model_init()
    model.load_weights('aggregated_models/%s_ep%d.h5'%(hostname,e))
    arr.append(copy.deepcopy(model.get_weights()))
    for p in glob.glob('trained_models/*_ep%d.h5'%(e)):
        model = utils.model_init()
        while not os.path.exists(p):
            try:
                model.load_weights(p)
            except:
                pass
        arr.append(copy.deepcopy(model.get_weights()))
    arr_avg = utils.aggregated(arr)
    aggregated_model = utils.model_init()
    aggregated_model.set_weights(arr_avg)
    aggregated_model.save_weights('aggregated_models/%s_ep%d.h5'%(hostname,e+1))
    utils.broadcast_model(trainer_ip,19192,'aggregated_models/%s_ep%d.h5'%(hostname,e+1), 'exchanged_models')


    # utils.send_model(national_ip,19190,'global_models/aggregated_model_ep%d.h5'%(e+1))
    # while not os.path.exists('aggregated_models/%s_ep%d.h5'%(ip,ep_counter)):
    #         time.sleep(5)