__author__ = 'Christoph Jansen, HTW Berlin'

import abc

class ACloudConnector():
    __metaclass__=abc.ABCMeta

    @abc.abstractmethod
    def createServer(self):
        """create a virtual server"""
        pass

    @abc.abstractmethod
    def destroyServer(self, id):
        """destroy a virtual server"""
        pass

    @abc.abstractmethod
    def listAllServerIDs(self):
        """list IDs of all a virtual servers running in the cloud"""
        pass

    def getConfig(self):
        """get config as dict"""
        pass

    @abc.abstractmethod
    def check(self):
        """check if connection works"""
        pass