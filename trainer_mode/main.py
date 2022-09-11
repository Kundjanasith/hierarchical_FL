import sys, os, time
sys.path.insert(1, '..')       
import utils

global_ip = '10.10.100.33'

ip = sys.argv[1]
NUM_ROUNDS = 10000

for e in range(NUM_ROUNDS):
    utils.receive_model('0.0.0.0',19191,'global_models/')
    model = utils.model_init()
    # model.load_weights('global_models/aggregated_model_ep%d.h5'%e)
    while not os.path.exists('global_models/aggregated_model_ep%d.h5'%e):
        try:
            model.load_weights('global_models/aggregated_model_ep%d.h5'%e)
        except:
            pass
    x_train, y_train = utils.sampling_data()
    model.compile(optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(x_train, y_train,epochs=5,batch_size=16,verbose=1,validation_split=0.2)
    model.save_weights('local_models/%s_ep%d.h5'%(ip,e))
    utils.send_model(global_ip,19192,'local_models/%s_ep%d.h5'%(ip,e))

