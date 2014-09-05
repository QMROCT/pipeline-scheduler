#!/bin/bash

NUM_OF_TESTS=3

for i in $(seq 1 1 ${NUM_OF_TESTS}); do
	bash /vagrant/pipeline-scheduler/tests/multitask.sh
	sleep 400
	mv /vagrant/pipeline-scheduler/timetest.csv /vagrant/pipeline-scheduler/tests/servers10_ttl1_maxactive1_docker_${i}.csv
done

