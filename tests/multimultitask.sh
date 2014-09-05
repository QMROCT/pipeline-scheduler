#!/bin/bash

NUM_OF_TESTS=10

for i in $(seq 1 1 ${NUM_OF_TESTS}); do
	bash /vagrant/pipeline-scheduler/tests/multitask.sh
	sleep 350
	mv /vagrant/pipeline-scheduler/timetest.csv /vagrant/pipeline-scheduler/tests/docker_servers10_par_${i}.csv
done

