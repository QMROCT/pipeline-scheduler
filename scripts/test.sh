#!/bin/bash

whoami=$(whoami)
pwd=$(pwd)

echo "${whoami} ${pwd} $@" > ~/test.txt