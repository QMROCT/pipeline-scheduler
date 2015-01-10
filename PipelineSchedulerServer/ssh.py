__author__ = 'Christoph Jansen, HTW Berlin'

import paramiko
from time import sleep
from helper import loadConfigurationFile

class SSH:
    def __init__(self):
        self.sshConfig = self.SSHConfiguration()

    def check(self):
        return self.sshConfig.check()

    def connect(self, ip):

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print 'ssh connect ' + str(ip) + ' ...'
        ready = False
        counter = 0

        while not ready:
            if(counter > self.sshConfig.MAX_CONNECTION_RETRIES):
                print 'connection refused'
                return None
            try:
                client.connect(ip, username=self.sshConfig.AUTH_USER, password=self.sshConfig.AUTH_PASSWORD, key_filename=self.sshConfig.AUTH_KEYFILE)
                ready = True
            except:
                counter += 1
                sleep(self.sshConfig.CONNECTION_RETRY_INTERVAL)
                #print 'retry ' + str(counter)

        print 'connection successful'

        return client

    def uploadFiles(self, client, files, localFolder, remoteFolder):
        sftp = client.open_sftp()

        for file in files:
            completeLocal = localFolder + '/' + file
            completeRemote = remoteFolder + '/' + file
            sftp.put(completeLocal, completeRemote)

        sftp.close()

    def executeCommand(self, client, command):
        stdin, stdout, sterr = client.exec_command(command)
        channel = stdout.channel
        status = channel.recv_exit_status()
        return stdout.readlines()

    def disconnect(self, client):
        client.close()

    class SSHConfiguration:
        def __init__(self):
            parameters = loadConfigurationFile('ssh')
            self.MAX_CONNECTION_RETRIES = parameters.get('MAX_CONNECTION_RETRIES', 1000)
            self.CONNECTION_RETRY_INTERVAL = parameters.get('CONNECTION_RETRY_INTERVAL', 5)
            self.AUTH_USER = parameters.get('AUTH_USER')
            self.AUTH_KEYFILE = parameters.get('AUTH_KEYFILE')
            self.AUTH_PASSWORD = parameters.get('AUTH_PASSWORD')

        def check(self):
            message = 'missing parameter in ssh.yaml: '
            if(self.AUTH_USER == None):
                print message + 'AUTH_USER'
                return False
            if(self.AUTH_KEYFILE == None and self.AUTH_PASSWORD == None):
                print message + 'either AUTH_KEYFILE or AUTH_PASSWORD'
                return False
            return True