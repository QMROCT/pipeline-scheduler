#!/bin/bash

if [[ ! -f "install.sh" ]]; then
	echo "ERROR: run install.sh from directory containing it"
	exit 1
fi

if [[ ! -d PipelineSchedulerServer ]]; then
	echo "ERROR: current directory must contain python module PipelineSchedulerServer"
	exit1
fi

SRC=$(pwd)
DEST=~/.pipeline-scheduler/

# copy configuration templates
[[ ! -d ${DEST} ]] && mkdir ${DEST}
cp *.yaml.template ${DEST}

# rename templates but do not override existing
cd ${DEST}
for file in *.yaml.template; do
	name=$(basename ${file} .yaml.template)
	if [[ ! -f ${name}.yaml ]]; then
		mv ${file} ${name}.yaml
	else
		rm ${file}
	fi
done

# add pipeline-scheduler to PYTHONPATH
echo "PYTHONPATH=\"\${PYTHONPATH}:${SRC}:${SRC}/PipelineSchedulerServer\"" >> ~/.bashrc
echo "export PYTHONPATH" >> ~/.bashrc

echo "PYTHONPATH=\"\${PYTHONPATH}:${SRC}:${SRC}/PipelineSchedulerServer\"" >> ~/.profile
echo "export PYTHONPATH" >> ~/.profile

source ~/.bashrc
