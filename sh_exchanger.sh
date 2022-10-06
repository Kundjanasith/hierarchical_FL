echo $1
cd exchanger_mode && screen -d -m -S se python3 server.py && screen -d -m -S e python3 main.py