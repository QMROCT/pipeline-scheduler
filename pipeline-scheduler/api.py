__author__ = 'Christoph Jansen, HTW Berlin'

from uuid import uuid4
from novaclient.client import Client
from cloud import Instance
from time import sleep
from thread import allocate_lock
from novaclient.v1_1.servers import Server

class Nova:

    lock = allocate_lock()

    def __init__(self, applicationHandler, credentials):
        self.applicationHandler = applicationHandler
        self.client = Client(**credentials)
        print credentials

    def selfCheck(self):
        try:
            self.client.servers.list()
        except:
            return False
        return True

    def createInstance(self):
        config = self.applicationHandler.config

        name = str(uuid4())

        nics = None
        if(config.VM_NETWORK_ID != None):
            nics = [{"net-id": config.VM_NETWORK_ID}]
        server = self.client.servers.create(name=name, image=config.VM_IMAGE_ID, flavor=config.VM_FLAVOR, key_name=config.VM_KEYPAIR_NAME, nics=nics)

        if(config.OS_USE_FLOATING_IP):
            self.lock.acquire()
            ip = self.getFloatingIP(config.OS_IP_POOL)
            if ip == None:
                self.lock.release()
                return None

            ready = False
            counter = 0
            while not ready:
                if(counter > config.MAX_CONNECTION_RETRIES):
                    print 'connection refused'
                    self.lock.release()
                    return None
                try:
                    server.add_floating_ip(address=ip)
                    ready = True
                except:
                    counter += 1
                    sleep(config.CONNECTION_RETRY_INTERVAL)

            self.lock.release()
        else:
            counter = 0

            networks = None

            while counter <= config.MAX_CONNECTION_RETRIES:
                server = self.client.servers.get(server.id)
                networks = server.networks
                if(networks):
                    break
                networks = None
                counter += 1
                sleep(config.CONNECTION_RETRY_INTERVAL)

            ip = networks['private'][0]
            print ip

        try:
            server.add_security_group(security_group=config.OS_SECURITY_GROUP)
        except:
            pass

        instance = Instance(server.id, name, ip, config.VM_INSTANCE_TTL, None)

        return instance

    def getFloatingIP(self, ipPool):
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
            return None

        return ip

    def deleteInstance(self, instance):
        try:
            self.client.servers.delete(instance.id)
            #self.client.floating_ips.delete(instance.ip)
        except:
            return False

        return True

    def deleteAllInstancesExcept(self, instances):

        try:
            servers = self.client.servers.list()

            for s in servers:
                id = s.id
                delete = True
                for i in list(instances):
                    if i.id == id:
                        delete = False
                        break
                if delete:
                    self.client.servers.delete(s)
        except:
            return False

        return True



