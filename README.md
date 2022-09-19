# Hierarchical Federarted Learning

## Docker Image
```
sudo docker run -it -p 19190:19190 -p 19191:19191 -p 19192:19192 kundjanasith/pik8ke_swarmlearning:hfl0.0.3
```

## Directory
```
.
|--exchanger_mode/
|   |--aggregated_models/
|   |--exchanged_models/
|   |--main.py
|   |--server.py 
|--aggregator_mode/
|   |--aggregated_models/
|   |--exchanged_models/
|   |--trained_models/
|   |--main.py
|   |--server.py 
|--trainer_mode/
|   |--exchanged_models/
|   |--trained_models/
|   |--main.py
|--utils.py
|--Dockerfile
|--config.ini
```

## Overview

![overview](figures/overview.png)

## Set up

![overview](figures/setup.png)


## Result

### Model accuracy
![accuracy_exchanger](figures/accuracy/exchanger.png)
![accuracy_aggregator](figures/accuracy/aggregator.png)
![accuracy_trainer](figures/accuracy/trainer.png)

### Execution time
![time_exchanger](figures/time/exchanger.png)
![time_aggregator](figures/time/aggregator.png)
![time_trainer](figures/time/trainer.png)

### Timeline
![timeline](figures/time/timeline_ep45.png)

## Comparison
![compare](figures/compare.png)

