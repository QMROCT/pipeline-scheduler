__author__ = 'Christoph Jansen, HTW Berlin'

import types
from Queue import Queue
from thread import allocate_lock

class CloudHandler:

    activeServers = {}
    queuedServers = Queue()

    lock = allocate_lock()

    def __init__(self, applicationConfig, connector):
        self.applicationConfig = applicationConfig
        self.connector = connector

    def deleteServersUntracked(self):
        # use with caution, can delete servers which are booting and not yet registered
        serverIDs = self.connector.listAllServerIDs()

        result = []

        for id in serverIDs:
            for k, v in self.activeServers.items():
                if k == id:
                    continue

            for i in list(self.queuedServers.queue):
                if i.id == id:
                    continue

            self.connector.destroyServer(id)
            result.append(id)

        return {'request': 'success', 'content': result}

    def retrieveServer(self):
        self.lock.acquire()
        if(not self.queuedServers.empty()):
            server = self.queuedServers.get()
            self.activeServers[server.id] = server
            self.lock.release()
            return server
        self.lock.release()

        server = self.connector.createServer()
        if(server == None):
            return None

        self.lock.acquire()
        self.activeServers[server.id] = server
        self.lock.release()
        return server

    def releaseServer(self, server):
        server.ttl = server.ttl - 1
        if(server.ttl < 1):
            self.connector.destroyServer(server.id)
            self.lock.acquire
            del self.activeServers[server.id]
            self.lock.release
        else:
            self.lock.acquire
            self.queuedServers.put(server)
            del self.activeServers[server.id]
            self.lock.release

    def getServers(self, input):
        if(input == None):
            return self._listServers()
        elif type(input) is types.ListType:
            return self._listServersByIDs(input)
        else:
            return {'request': 'error', 'content': 'accepts empty input, or list of IDs'}

    def _listServers(self):
        self.lock.acquire()
        active = []
        for k, v in self.activeServers.items():
            active.append(v.__dict__)
        queued = []
        for i in list(self.queuedServers.queue):
            queued.append(i.__dict__)
        self.lock.release()
        return {'request': 'success', 'content': {'active': active, 'queued': queued}}

    def _listServersByIDs(self, input):
        results = []
        for id in input:
            result = self._serverByID(id)
            if(result != None):
                results.append(result)

        return {'request': 'success', 'content': results}

    def _serverByID(self, id):
        self.lock.acquire()
        for k, v in self.activeServers.items():
            if k == id:
                self.lock.release()
                return {'status': 'active', 'server': v.__dict__}

        for i in list(self.queuedServers.queue):
            if i.id == id:
                self.lock.release()
                return {'status': 'queued', 'server': i.__dict__}

        self.lock.release()
        return None