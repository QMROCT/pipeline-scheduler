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

class TimeStopper:

    def __init__(self, initialTimestamp):
        self.initialTimestamp = initialTimestamp
        self.stopped = []

    def stop(self):
        diff = time() - self.initialTimestamp
        for val in self.stopped:
            diff -= val
        self.stopped.append(diff)

    def writeDataToCSV(self, filePath):
        if(len(self.stopped) < 3):
            return
        if(filePath == None):
            return
        if(not os.path.isfile(filePath)):
            self._initializeCSV(filePath)

        s = '\n'
        i = 0
        while i < 3:
            s += str(self.stopped[i]) + ';'
            i += 1
        s += str(self._calculateTotal())
        with open(filePath, 'a') as f:
            f.write(s)

    def _calculateTotal(self):
        result = 0
        for val in self.stopped:
            result += val
        return result

    def _initializeCSV(self, filePath):
        s = 'serverStart;serverUp;processingDone,total'
        with open(filePath, 'w') as f:
            f.write(s)

