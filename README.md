## Pipeline Scheduler

[Flask](http://flask.pocoo.org/) server to schedule and process [XNAT](http://www.xnat.org/) pipelines with [OpenStack](http://www.openstack.org/).

### Requirements

* Linux
* Bash
* Python >= 2.6 (not 3.x)


### Installation

```bash
git clone https://github.com/QMROCT/pipeline-scheduler
cd pipeline-scheduler
bash install.sh
cd ~/.pipeline-scheduler
# edit all configuration files with .yaml extension in this directory to fit your installation
# install all python package dependencies by hand
# see documentation for more information
```

### Python Dependencies
* [Flask](http://flask.pocoo.org/)
* [Paramiko](http://www.paramiko.org/)
* [PyYAML](http://pyyaml.org/)
* [NovaClient](https://github.com/openstack/python-novaclient/)


### Server Start

```bash
cd pipeline-scheduler
python PipelineSchedulerServer
```


### Parameter configuration for .yaml files

application.yaml

```yaml
# number of tasks which can be processed at a time
# not required - default: 1
MAX_ACTIVE_TASKS: 1

# time to live specifies number of times a VM will be reused for different tasks
# not required - default: 1
VIRTUAL_SERVER_TTL: 1

# name of cloud connection client to be used
# not required - default: nova
CONNECTOR: 'nova'

# folder which contains scripts or other files required for task
# required
LOCAL_SCRIPTS_FOLDER: '/vagrant/pipeline-scheduler/scripts'

# location in VM to upload scripts or other files to
# required
REMOTE_BASE_FOLDER: '/home/ubuntu'

# file to log VM startup times to
# not required - default: null
TIMETEST_CSV_FILE: 'timetest.csv'

# host ip for flask server
# required
HOST: '0.0.0.0'

# port for flask server
# required
PORT: 8100
```

ssh.yaml

```yaml
# number of retries in waiting loops
# not required - default: 1000
MAX_CONNECTION_RETRIES: 1000

# number of seconds to wait after each retry
# not required - default: 5
CONNECTION_RETRY_INTERVAL: 5

# user for ssh authentication
# required
AUTH_USER: 'ubuntu'

# keyfile for ssh authentication
# required if AUTH_PASSWORD is null
AUTH_KEYFILE: '/home/vagrant/.ssh/id_rsa'

# password for ssh authentication
# required if AUTH_KEYFILE is null
AUTH_PASSWORD: null
```

nova.yaml

```yaml
# number of retries in waiting loops
# not required - default: 1000
MAX_CONNECTION_RETRIES: 1000

# number of seconds to wait after each retry
# not required - default: 5
CONNECTION_RETRY_INTERVAL: 5

# id of openstack flavor for VM
# required
FLAVOR: 2

# name of openstack keypair added to VM on startup (requires cloud init)
# not required - default: null
AUTH_KEYNAME: 'test_key'

# name of openstack security group added to running VM
# not required - default: null
SECURITY_GROUP: 'SSH_ALLOWED'

# boolean specifying if public floating ip should be used instead of private ip
# not required - default: False
USE_FLOATING_IP: True

# name of ip pool for floating ip
# not required - default: null
IP_POOL: null

# id of openstack network for VM
# not required - default: null
NETWORK_ID: null

# credentials file to authenticate nova client
# required - must contain environment variables OS_USERNAME, OS_PASSWORD, OS_AUTH_URL, OS_TENANT_NAME
CREDENTIALS_FILE: '/home/vagrant/devstack/openrc'

# id of VM image
# required
IMAGE_ID: 'e7fb1f98-621f-4dee-b589-3f128d660d65'
```

### Pipeline-Scheduler Web-API Documentation

Pipeline-Scheduler is controlled by sending requests to its Web-API. This Documentation describes the meaning of the URL paths and the supported HTTP functions. The Web-API accepts well formatted JSON objects, usually a Dictionary or a List of Dictionaries, and returns JSON objects. For the API functions cURL commands (Bash) are given as reference.

```bash
# definition of sample variables
server="${flask_ip}:${flask_port}" # defined in config
session="SampleSession" # XNAT specific
project="SampleProject" # XNAT specific
subject="SampleSubject" # XNAT specific
host="http://${xnat_ip}:${xnat_port}/xnat/" # XNAT installation
user="admin" # XNAT authentication
pwd="admin" # XNAT authentication
script="qmroct.sh" # script conained in LOCAL_SCRIPTS_FOLDER (see config) to be executed in cloud VM
type="xnat" # XNATPipeline is one possible kind of task
```

/tasks GET
```bash
# list all active and queued tasks
# input: null
curl ${server}/tasks

# list tasks by ID
# input: list containing IDs
curl -H 'Content-Type: application/json' -d '["'${id}'","'${id}'"]' "${server}/tasks"
```

/tasks PUSH
```bash
# register single task
# input: dictionary with task parameters - every task must contain parameter type
curl -X POST -H 'Content-Type: application/json' -d '{"project":"'${project}'","subject":"'${subject}'","session":"'${session}'","host":"'${host}'","user":"'${user}'","pwd":"'${pwd}'","script":"'${script}'","type":"'${type}'"}' "${server}/tasks"

# register multiple tasks
# input: list of dictionaries with task parameters
curl -X POST -H 'Content-Type: application/json' -d '[{"project":"'${project}'","subject":"'${subject}'","session":"'${session}'","host":"'${host}'","user":"'${user}'","pwd":"'${pwd}'","script":"'${script}'","type":"'${type}'"},{"project":"'${project}'","subject":"'${subject}'","session":"'${session}'","host":"'${host}'","user":"'${user}'","pwd":"'${pwd}'","script":"'${script}'","type":"'${type}'"}]' "${server}/tasks"
```

/servers GET
```bash
# list all active and queued virtual servers, which are handled by Pipeline-Scheduler
# input: null
curl ${server}/servers

# list virtual servers by IDs
# input: list containing IDs
curl -H 'Content-Type: application/json' -d '["'${id}'","'${id}'"]' "${server}/servers"
```

/servers/untracked DELETE
```bash
# delete all virtual servers in OpenStack project, which are NOT handled by Pipeline-Scheduler, to free resources
# input: null
curl -X DELETE ${server}/servers/untracked
```

/config GET
```bash
# list configurations, which have been loaded from .yaml files
# input: null
curl ${server}/config
```

/config PUT
```bash
# update configurations, by reloading .yaml files
# input: null
curl -X PUT ${server}/config
```

### Secure Authentication

A simple authentication mechanism using string tokens has been implemented and is able to secure the web api. In order to activate it, simply create the file ~/.pipeline-scheduler/tokens and add a password token to the first line of the file. When accessing the api send the authentication token as URL parameter (not JSON!) like so:

```bash
curl ${server}?token=YourAuthenticationToken
```

There can be several valid authetication tokens at a time, by adding them to the tokens file line by line.

The Pipeline Scheduler needs to be restarted after adding or deleting tokens.

Reminder: Always use TLS to secure the web api (for example by using an Apache Webserver with proper TLS configuration as proxy).

### Not yet implemented

* Advanced error handling
* Logging
* Supporting multiple VM-Images for different Tasks
* Source code documentation
* More Web-API functions
