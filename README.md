# Docker-Easy-Scaler

Container which dynamically scales your different containers based on per container type metric, such as rabbitmq queues

#### Docker Setup Commands
```python
docker build -t docker-easy-scaler:latest .

docker run -d \
    --name docker-easy-scaler \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /home/administrator/docker/containers/docker-easy-scaler/config:/config \
    --network "bindaysapistack_bindays-api-network" \
    --restart on-failure \
    docker-easy-scaler
```

#### Config Layout
```json
{
    "Containers": [
        {
            "Minimum-Count": 3,
            "Docker-Configuration": {
                "Name": "bindays-worker-collectors",
                "Image": "bindays-worker-generic:latest",
                "Network": "bindaysapistack_bindays-api-network",
                "Environment": {
                    "WORKER_TYPE": "Collectors"
                },
                "Restart Policy": {
                    "Name": "on-failure", 
                    "MaximumRetryCount": 5
                },
                "Detach": true
            },
            "Metric-Tool": {
                "Type": "RabbitMQ",
                "IP-Address": "172.28.1.1",
                "Port": "5672",
                "RMQ-Queue": "Collectors"
            },
            "Check-Frequency-Seconds": 0.1,
            "Creation": {
                "Value": 1,
                "Cooldown": 10
            },
            "Destruction": {
                "Value": 5,
                "Cooldown": 30
            }
        }
    ]
}
```
