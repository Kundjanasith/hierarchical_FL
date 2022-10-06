echo $1
cd aggregator_mode && screen -d -m -L -S sa python3 server.py && screen -d -m -L -S a python3 main.py $1