__author__ = 'Christoph Jansen, HTW Berlin'

from time import time
import os

class VirtualServer:

    timestamp = time()

    def __init__(self, id, name, ip, ttl=1):
        self.id = id
        self.name = name
        self.ip = ip
        self.ttl = ttl

class TimeTest:

    def __init__(self, instanceStart=None, instanceUp=None, processingStart=None, processingDone=None):
        self.instanceStart = instanceStart
        self.instanceUp = instanceUp
        self.processingStart = processingStart
        self.processingDone = processingDone

    def writeDataToCSV(self, filePath):
        if(filePath == None):
            return
        if(not os.path.isfile(filePath)):
            self._initializeCSV(filePath)
        s = '\n' + str(self.instanceStart) + ';' + str(self.instanceUp) + ';' + str(self.processingStart) + ';' + str(self.processingDone)
        with open(filePath, 'a') as f:
            f.write(s)

    def _initializeCSV(self, filePath):
        s = 'instanceStart;instanceUp;processingStart;processingDone'
        with open(filePath, 'w') as f:
            f.write(s)

