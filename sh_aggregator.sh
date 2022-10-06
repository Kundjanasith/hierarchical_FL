echo $1
cd aggregator_mode && screen -d -m -S sa python3 server.py && screen -d -m -S a python3 main.py $1