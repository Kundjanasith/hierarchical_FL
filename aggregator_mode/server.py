import sys, os, time, glob, copy
sys.path.insert(1, '..')       
import utils

# NUM_ROUNDS = 10
# for e in range(NUM_ROUNDS):
#     for n in range(len(local_ip)):
#         utils.receive_model('0.0.0.0',19192,'local_models/')

while True:
    utils.receive_model('0.0.0.0',19192,'local_models/')