
import multiprocessing
import json
import docker
import copy
import random
import time
from pyrabbit.api import Client

class ContainerMonitor:

    def __init__(self, config):
        
        self.config = config
        self.Process_Setup.start()

    def Setup(self):
        print("Setting up Container Monitor...")

        self.creationCooldown = self.config["Creation"]["Cooldown"]
        self.destructionCooldown = self.config["Destruction"]["Cooldown"]

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

        self.pyrabbitClient = Client(f"{self.config['Metric-Tool']['IP-Address']}:{self.config['Metric-Tool']['RMQ-Management-Port']}", "guest", "guest")

    def Disconnect(self):

        pass

    def Suicide(self):

        pass

    def Watch(self):
        print("Beginning Watch...")

        while True:
            
            currentQueueLength = self.pyrabbitClient.get_queue_depth('/', self.config["Metric-Tool"]["RMQ-Queue"])

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

        containerToRemove = self.GetContainersOfType()[-1]
        
        containerToRemove.stop()
        print("Container Stopped...")

        for i in range(60):

            try:
                containerToRemove.remove()
                print("Container Removed...")
                break
            except:
                pass

            time.sleep(1)


def GenerateContainerMonitors(configPath):
    print("Generating Container Monitors...")

    configFile = open(configPath, "r")
    config = json.load(configFile)

    containerMonitors = {}

    for containerConfig in config["Containers"]:

        containerMonitors[containerConfig["Docker-Configuration"]["Name"]] = ContainerMonitor(containerConfig)

        if containerConfig["Stage-Monitor-Creation"] == True:
            
            time.sleep(containerConfig["Check-Frequency-Seconds"]/ len(config["Containers"]))

GenerateContainerMonitors("/config/config.json")