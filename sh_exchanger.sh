echo $1
cd exchanger_mode && screen -d -m -L -S se python3 server.py && screen -d -m -L -S e python3 main.py