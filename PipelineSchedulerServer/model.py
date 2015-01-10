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

    numOfStops = 3 # serverStart, serverUp, processingDone

    def __init__(self, initialTimestamp):
        self.initialTimestamp = initialTimestamp
        self.stopped = []

    def stop(self):
        diff = time() - self.initialTimestamp
        for val in self.stopped:
            diff -= val
        self.stopped.append(diff)

    def writeDataToCSV(self, filePath):
        if(len(self.stopped) < self.numOfStops):
            return
        if(filePath == None):
            return
        if(not os.path.isfile(filePath)):
            self._initializeCSV(filePath)

        s = '\n'
        i = 0
        while i < self.numOfStops:
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
        s = 'serverStart;serverUp;processingDone;total'
        with open(filePath, 'w') as f:
            f.write(s)

class TimeLogger:

    def __init__(self):
        self.data = '\n'

    def _initializeCSV(self, filePath):
        s = 'server_start;script_upload;script_start;dicom_download_start;algo1_processing_start;algo1_upload_start;algo2_processing_start;algo2_upload_start;algo3_processing_start;algo3_uload_start;script_stop'
        with open(filePath, 'w') as f:
            f.write(s)

    def appendData(self, time):
        self.data += str(time) + ' '

    def writeDataToCSV(self, filePath):
        if(filePath == None):
            return
        if(not os.path.isfile(filePath)):
            self._initializeCSV(filePath)
        with open(filePath, 'a') as f:
            f.write(self.data)

