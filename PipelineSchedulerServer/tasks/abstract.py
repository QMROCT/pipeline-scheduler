__author__ = 'Christoph Jansen, HTW Berlin'

import abc

class ATask():
    __metaclass__=abc.ABCMeta

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
