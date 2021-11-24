# Docker-Easy-Scaler

Container which dynamically scales your different containers based on per container type metric, such as rabbitmq queues

```json
{
    "Check-Frequency-Ms": 0.1,
    "Containers": [
        {
            "Docker-Command": "",
            "Container-Name": "",
            "Container-Image": "",
            "Metric-Tool": "RMQ",
            "RMQ-Queue": "XXX",
            "Creation": {
                "Value": 10,
                "Cooldown": 30,
            },
            "Destruction": {
                "Value": 10,
                "Lifetime": 30,
            }
        }
    ]
}
```
