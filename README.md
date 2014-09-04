## Pipeline Scheduler

[Flask](http://flask.pocoo.org/) server to schedule and process [XNAT](http://www.xnat.org/) pipelines with [OpenStack](http://www.openstack.org/).


### Installation

```bash
git clone https://github.com/QMROCT/pipeline-scheduler
cd pipeline-scheduler
bash install.sh
cd ~/.pipeline-scheduler
# edit all configuration files with .yaml extension to fit your installation
# install all python package dependencies by hand
```

### Python Dependencies
* [Flask](http://flask.pocoo.org/)
* [Paramiko](http://www.paramiko.org/)
* [PyYAML](http://pyyaml.org/)
* [NovaClient](https://github.com/openstack/python-novaclient/)


### Server Start

```bash
python PipelineSchedulerServer
```


### Parameter Documentation: config.yaml

TODO

### Pipeline-Scheduler Web-API Documentation

Pipeline-Scheduler is controlled by sending requests to its Web-API. This Documentation describes the meaning of the URL paths and the supported HTTP functions. The Web-API accepts well formatted JSON objects, usually a Dictionary or a List of Dictionaries, and returns JSON objects. For the API functions cURL commands (Bash) are given as reference.

```bash
# definition of sample variables
server="${flask_ip}:${flask_port}" # defined in config
session="ncrc_S01323" # XNAT specific
project="test" # XNAT specific
subject="XNAT_S00013" # XNAT specific
host="http://${xnat_ip}:${xnat_port}/xnat/" # XNAT installation
user="admin" # XNAT authentication
pwd="admin" # XNAT authentication
script="qmroct.sh" # script conained in LOCAL_SCRIPTS_FOLDER (see config) to be executed in cloud VM
type="xnat"
```

/tasks GET
```bash
# list all active and queued tasks - XNATPipeline is one possible kind of task (parameter "type" must be set to "xnat")
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

### Not yet implemented

* Advanced error handling
* Logging
* Source code documentation
* More Web-API functions
