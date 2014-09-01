## Pipeline Scheduler

[Flask](http://flask.pocoo.org/) server to schedule and process [XNAT](http://www.xnat.org/) pipelines with [OpenStack](http://www.openstack.org/).


### Installation

```bash
mkdir ~/.pipeline-scheduler
cp config.yaml.template ~/.pipeline-scheduler/config.yaml
# edit ~/.pipeline-scheduler/config.yaml
```

### Python Dependencies
* [Flask](http://flask.pocoo.org/)
* [Paramiko](http://www.paramiko.org/)
* [PyYAML](http://pyyaml.org/)
* [NovaClient](https://github.com/openstack/python-novaclient/)


### Server Start

```bash
python pipeline-scheduler
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
```

/pipeline GET
```bash
# list all active and queued pipelines
# input: null
curl ${server}/pipeline
```

/pipeline PUSH
```bash
# register one pipeline
# input: dictionary
curl -X POST -H 'Content-Type: application/json' -d '{"project":"'${project}'","subject":"'${subject}'","session":"'${session}'","host":"'${host}'","user":"'${user}'","pwd":"'${pwd}'","script":"'${script}'"}' "${server}/pipeline"

# register multiple pipelines
# input: list of dictionaries
curl -X POST -H 'Content-Type: application/json' -d '[{"project":"'${project}'","subject":"'${subject}'","session":"'${session}'","host":"'${host}'","user":"'${user}'","pwd":"'${pwd}'","script":"'${script}'"},{"project":"'${project}'","subject":"'${subject}'","session":"'${session}'","host":"'${host}'","user":"'${user}'","pwd":"'${pwd}'","script":"'${script}'"}]' "${server}/pipeline"
```

/instance GET
```bash
# list all active and queued virtual servers
# input: null
curl ${server}/instance
```

/instance DELETE
```bash
# delete all instances in OpenStack project, which are NOT handled by Pipeline-Scheduler, to free resources
# input: null
curl -X DELETE ${server}/instance
```

### Not yet implemented

* Advanced error handling
* Logging
* Seperate config files for different cloud APIs
* Source code documentation
* More Web-API functions
* OpenStack HEAT support
