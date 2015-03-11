__author__ = 'Christoph Jansen, HTW Berlin'

from os.path import expanduser
import yaml, subprocess, os

def loadConfigurationFile(name):
    home = expanduser("~")
    if home[-1:] == '\n':
        home = home[:-1]
    configPath = home + '/.pipeline-scheduler/' + name + '.yaml'

    try:
        stream = open(configPath, 'r')
        doc = yaml.load(stream)
        stream.close()
    except:
        print 'could not load ' + configPath
        return {}

    print name + '.config: ' + str(doc)

    return doc

def sourceFile(filePath):
    try:
        command = ['bash', '-c', 'source ' + filePath + ' && env']
        proc = subprocess.Popen(command, stdout = subprocess.PIPE)

        for line in proc.stdout:
          (key, _, value) = line.partition("=")
          os.environ[key] = value

        proc.communicate()
    except:
        print 'could not parse ' + filePath
        return False

    return True

def loadTokens():
    home = expanduser("~")
    if home[-1:] == '\n':
        home = home[:-1]
    tokenPath = home + '/.pipeline-scheduler/tokens'
    tokens = []
    with open(tokenPath, 'r') as f:
        for line in f:
            tokens.append(line.rstrip())
    return tokens