__author__ = 'Christoph Jansen, HTW Berlin'

import os, types
from uuid import uuid4
from novaclient.client import Client
from time import sleep
from thread import allocate_lock
from PipelineSchedulerServer.model import VirtualServer
from PipelineSchedulerServer.helper import loadConfigurationFile, sourceFile
from abstract import ACloudConnector

class Nova(ACloudConnector):

    lock = allocate_lock()

    def __init__(self, applicationConfig):
        self.applicationConfig = applicationConfig
        self.novaConfig = self.NovaConfiguration()
        if(not self.novaConfig.check()):
            return
        credentials = self._retrieveCredentials()
        if(credentials == None):
            return
        self.client = Client(**credentials)

    def _retrieveCredentials(self):
        if (not sourceFile(self.novaConfig.CREDENTIALS_FILE)):
            return None

        username = os.environ.get('OS_USERNAME')
        api_key = os.environ.get('OS_PASSWORD')
        auth_url = os.environ.get('OS_AUTH_URL')
        project_id = os.environ.get('OS_TENANT_NAME')
        version = '1.1'

        credentials = {'username':username, 'api_key':api_key, 'auth_url':auth_url, 'project_id': project_id, 'version': version}

        for k, v in credentials.items():
            if(v == None):
                print 'could not find key ' + str(k) + ' in credentials file ' + self.novaConfig.CREDENTIALS_FILE
                return None
            if(v[-1:] == '\n'):
                credentials[k] = v[:-1]

        print 'nova credentials: ' + str(credentials)
        return credentials

    def check(self):
        try:
            self.client.servers.list()
        except:
            print 'could not connect to nova'
            return False
        return True

    def getConfig(self):
        return self.novaConfig.__dict__

    def createServer(self):
        name = str(uuid4())

        nics = None
        if(self.novaConfig.NETWORK_ID != None):
            nics = [{"net-id": self.novaConfig.NETWORK_ID}]
        server = self.client.servers.create(name=name, image=self.novaConfig.IMAGE_ID, flavor=self.novaConfig.FLAVOR, key_name=self.novaConfig.AUTH_KEYNAME, nics=nics)

        if(self.novaConfig.USE_FLOATING_IP):
            self.lock.acquire()
            ip = self._getFloatingIP()
            if ip == None:
                self.lock.release()
                return None

            ready = False
            counter = 0
            while not ready:
                if(counter > self.novaConfig.MAX_CONNECTION_RETRIES):
                    print 'could not add floating ip to virtual server'
                    self.lock.release()
                    return None
                try:
                    server.add_floating_ip(address=ip)
                    ready = True
                except:
                    counter += 1
                    sleep(self.novaConfig.CONNECTION_RETRY_INTERVAL)

            self.lock.release()
        else:
            counter = 0

            networks = None

            while counter <= self.novaConfig.MAX_CONNECTION_RETRIES:
                server = self.client.servers.get(server.id)
                networks = server.networks
                if(networks):
                    break
                networks = None
                counter += 1
                sleep(self.novaConfig.CONNECTION_RETRY_INTERVAL)

            ip = networks['private'][0]
            print ip

        try:
            server.add_security_group(security_group=self.novaConfig.SECURITY_GROUP)
        except:
            print 'could not add security group ' + self.novaConfig.SECURITY_GROUP

        virtualServer = VirtualServer(id=server.id, name=name, ip=ip, ttl=self.applicationConfig.VIRTUAL_SERVER_TTL)

        return virtualServer

    def destroyServer(self, id):
        try:
            self.client.servers.delete(id)
        except:
            print 'could not destroy virtual server ' + id
            return False

        return True

    def listAllServerIDs(self):
        result = []

        try:
            servers = self.client.servers.list()
            for s in servers:
                result.append(s.id)
        except:
            print 'could not list virtual servers'
            pass

        return result

    def _getFloatingIP(self):
        ipPool = self.novaConfig.IP_POOL
        ip = None
        try:
            ips = self.client.floating_ips.list()
            if(ipPool != None):
                for i in list(ips):
                    if (i.pool == ipPool and i.instance_id == None):
                        ip = i.ip
                        break
                if (ip == None):
                    ip = self.client.floating_ips.create(pool = ipPool)
            else:
                for i in list(ips):
                    if (i.instance_id == None):
                        ip = i.ip
                        break
                if (ip == None):
                    ip.ip = self.client.floating_ips.create(pool = None)
        except:
            print 'could not retrieve floating ip'
            return None

        return ip

    class NovaConfiguration:
        def __init__(self):
            parameters = loadConfigurationFile('nova')
            self.MAX_CONNECTION_RETRIES = parameters.get('MAX_CONNECTION_RETRIES', 100)
            self.CONNECTION_RETRY_INTERVAL = parameters.get('CONNECTION_RETRY_INTERVAL', 5)
            self.FLAVOR = parameters.get('FLAVOR')
            self.AUTH_KEYNAME = parameters.get('AUTH_KEYNAME')
            self.SECURITY_GROUP = parameters.get('SECURITY_GROUP')
            self.USE_FLOATING_IP = parameters.get('USE_FLOATING_IP')
            self.IP_POOL = parameters.get('IP_POOL')
            self.NETWORK_ID = parameters.get('NETWORK_ID')
            self.CREDENTIALS_FILE = parameters.get('CREDENTIALS_FILE')
            self.IMAGE_ID = parameters.get('IMAGE_ID')

        def check(self):
            message = 'missing parameter in nova.yaml: '
            if(self.FLAVOR == None):
                print message + 'FLAVOR'
                return False
            if(self.SECURITY_GROUP == None):
                print message + 'SECURITY_GROUP'
                return False
            if(self.USE_FLOATING_IP == None):
                print message + 'USE_FLOATING_IP'
                return False
            if(self.CREDENTIALS_FILE == None):
                print message + 'CREDENTIALS_FILE'
                return False
            if(self.IMAGE_ID == None):
                print message + 'IMAGE_ID'
                return False
            return True
