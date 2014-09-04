__author__ = 'Christoph Jansen, HTW Berlin'

import abc
from uuid import uuid4
from time import time

class ATask(metaclass=abc.ABCMeta):

    id = str(uuid4())
    timestamp = time()

    @abc.abstractmethod
    def getFiles(self, remoteBaseFolder):
        """get files to upload to virtual server"""
        pass

    @abc.abstractmethod
    def getCommand(self):
        """get command to run on virtual server"""
        pass

    @abc.abstractmethod
    def check(self):
        """check if correctly initialized"""
        pass
