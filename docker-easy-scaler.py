
import multiprocessing
import pika
import json
import docker
import copy
import random
import time

class ContainerMonitor:

    def __init__(self, config):
        
        self.config = config
        self.Process_Setup.start()

    def Setup(self):
        print("Setting up Container Monitor...")

        self.creationCooldown = 0
        self.destructionCooldown = 0

        self.dockerClient = docker.from_env()

        self.Connect()
        self.CleanDockerConfigration()
        self.Watch()

    @property
    def Process_Setup(self):
        return multiprocessing.Process(target=self.Setup)

    def CleanDockerConfigration(self):

        self.config["Docker-Configuration"] = {k.lower().replace(" ","_").replace("-","_"): v for k, v in self.config["Docker-Configuration"].items()}

    def Connect(self):
        print("Connecting...")

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.config["Metric-Tool"]["IP-Address"],
                port=self.config["Metric-Tool"]["Port"]
            )
        )
        self.channel = self.connection.channel()
        self.queue = self.channel.queue_declare(self.config["Metric-Tool"]["RMQ-Queue"])

    def Disconnect(self):

        pass

    def Suicide(self):

        pass

    def Watch(self):
        print("Beginning Watch...")

        while True:

            currentQueueLength = self.queue.method.message_count

            if (currentQueueLength > self.config["Creation"]["Value"] or len(self.GetContainersOfType()) < self.config["Minimum-Count"]) and self.creationCooldown <= 0:

                self.Create()
                self.creationCooldown = self.config["Creation"]["Cooldown"]

            elif currentQueueLength < self.config["Destruction"]["Value"] and self.destructionCooldown <= 0 and len(self.GetContainersOfType()) > self.config["Minimum-Count"]:

                self.Delete()
                self.destructionCooldown = self.config["Destruction"]["Cooldown"]

            time.sleep(self.config["Check-Frequency-Seconds"])
            self.creationCooldown -= self.config["Check-Frequency-Seconds"]
            self.destructionCooldown -= self.config["Check-Frequency-Seconds"]

    def GetContainersOfType(self, attempts=0):

        if attempts > 10:
            return []

        try:

            containers = self.dockerClient.containers.list()

            containersOfType = []

            for container in containers:

                if self.config["Docker-Configuration"]["name"] in container.name:

                    containersOfType.append(container)

            return containersOfType

        except:
            GetContainersOfType(self, attempts=attempts + 1)

    def Create(self):
        print("Creating New Container...")

        randomNumberString = ''.join(random.choice('0123456789') for i in range(5))

        temporaryContainerDockerConfiguration = copy.deepcopy(self.config["Docker-Configuration"])
        currentNumberOfContainers = len(self.GetContainersOfType())
        temporaryContainerDockerConfiguration["name"] = temporaryContainerDockerConfiguration["name"] + f"-{currentNumberOfContainers}-{randomNumberString}"

        self.dockerClient.containers.run(**temporaryContainerDockerConfiguration)

    def Delete(self):
        print("Deleting Existing Container...")

        currentContainers = self.GetContainersOfType()

        currentContainers[-1].remove()


def GenerateContainerMonitors(configPath):
    print("Generating Container Monitors...")

    configFile = open(configPath, "r")
    config = json.load(configFile)

    containerMonitors = {}

    for containerConfig in config["Containers"]:

        containerMonitors[containerConfig["Docker-Configuration"]["Name"]] = ContainerMonitor(containerConfig)


GenerateContainerMonitors("/config/config.json")