#!/bin/bash

LC_NUMERIC=C

#XNAT_CACERT_FILE="path"
#WORK_DIR="/home/ubuntu/work"
#ASSESTS_DIR="/home/ubuntu/assets"
#MATLAB_HOME="/opt/mcr/v82"

err() {
    cd
	[ ! -z ${WORK_DIR} ] && [ -d "${WORK_DIR}" ] && rm -r ${WORK_DIR}
	echo "{'status': 'error', 'content': '$@'}" >&2
	exit 1
}

# get input parameters
while [ $# -gt 1 ]
do
	case $1 in
	-session)
	session="${2}"
	shift 2
	;;
	-subject)
	subject="${2}"
	shift 2
	;;
	-project)
	project="${2}"
	shift 2
	;;
	-host)
	host="${2}"
	shift 2
	;;
	-user)
	user="${2}"
	shift 2
	;;
	-pwd)
	pwd="${2}"
	shift 2
	;;
	*)
	shift 2
	;;
	esac
done

if [ -z ${WORK_DIR} ]; then
	err "WORK_DIR variable not found"
fi

[ -d ${WORK_DIR} ] && rm -r ${WORK_DIR}
mkdir ${WORK_DIR}

if [ -z ${ASSETS_DIR} ] || [ ! -d ${ASSETS_DIR} ]; then
	err "ASSETS_DIR variable or directory not found"
fi

if [ -z ${MATLAB_HOME} ] || [ ! -d ${MATLAB_HOME} ]; then
	err "MATLAB_HOME variable or directory not found"
fi

if [ -z ${session} ] || [ -z ${subject} ] || [ -z ${project} ] || [ -z ${host} ] || [ -z ${user} ] || [ -z ${pwd} ]; then
	err "At least one crucial argument not found or empty"
fi

if [ -z ${XNAT_CACERT_FILE} ] || [ ! -f ${XNAT_CACERT_FILE} ]; then
	XNAT_CACERT_FILE="-k"
else
	XNAT_CACERT_FILE="--cacert ${XNAT_CACERT_FILE}"
fi

# format host string if necessary
if [ $(echo ${host} | tail -c 2) == "/" ]; then
	host=$(echo ${host} | head -c -2)
fi

cd ${WORK_DIR}

session_folder="${project}_${subject}_${session}"

mkdir ${session_folder}
cd ${session_folder}

# get scan IDs from xnat image session
echo ${XNAT_CACERT_FILE}

TIME=$(date +%s)
LOG="${TIME}"

curl ${XNAT_CACERT_FILE} -u ${user}:${pwd} "${host}/REST/projects/${project}/subjects/${subject}/experiments/${session}/scans?format=csv" > "scans.info"
opt_scan=$(cat "scans.info" | grep "optScanData" | awk 'BEGIN {FS="," }{print $2}' | sed 's/"//; s/"//')
op_scan=$(cat "scans.info" | grep "opScanData" | awk 'BEGIN {FS="," }{print $2}' | sed 's/"//; s/"//')
if [ -z ${op_scan} ]; then
	op_scan=$(cat "scans.info" | grep "otherDicomScanData" | awk 'BEGIN {FS="," }{print $2}' | sed 's/"//; s/"//')
fi

rm "scans.info"

if [ ! -z ${opt_scan} ] && [ ! -z ${op_scan} ]; then
	scans="${opt_scan},${op_scan}"
elif [ ! -z ${opt_scan} ]; then
	scans="${opt_scan}"
elif [ ! -z ${op_scan} ]; then
	scans="${op_scan}"
fi

if [ -z ${scans} ]; then
	err "no OPT scan or OP scan found in session"
fi

# download and unzip scans
curl ${XNAT_CACERT_FILE} -O -u ${user}:${pwd} "${host}/REST/projects/${project}/subjects/${subject}/experiments/${session}/scans/${scans}/resources/DICOM/files?format=zip"

unzip "files?format=zip"
rm "files?format=zip"
files=$(find "." -type f -name "*")

# get scan paths
for i in ${files}; do
    modality=$(gdcmdump ${i} | grep "Modality" | awk '{print $3}' | sed 's/\[//; s/\]//')
    if [ ${modality} == "OPT" ]; then
        opt_file="${WORK_DIR}/${session_folder}/${i}"
    fi
    if [ ${modality} == "OP" ] || [ ${modality} == "OT" ]; then
        op_file="${WORK_DIR}/${session_folder}/${i}"
    fi
done

if [ -z ${opt_file} ] && [ -z ${op_file} ]; then
	err "OPT scan and OP scan both missing after extracting .zip file"
fi

# check for algorithms

cd "${ASSETS_DIR}/executables"

algorithms=$(find "${ASSETS_DIR}/executables" -type f -name "*.properties")

# execute all algorithms with downloaded scans
for i in ${algorithms}; do

    TIME=$(date +%s)
    LOG="${LOG} ${TIME}"

	valid=true
	algo_name=$(basename ${i} | sed 's/.\///' | awk 'BEGIN {FS="." } {print $1}')

	if [ ${algo_name} == "default" ]; then
		continue
	fi
	algo_version=$(cat ${i} | grep "version" | awk 'BEGIN {FS="=" } {print $2}')
	if [ -z ${algo_version} ]; then
		continue
	fi

	run="bash ${ASSETS_DIR}/executables/run_${algo_name}.sh ${MATLAB_HOME}"

	# check which parameters are needed to execute the algorithm
	for row in $(cat ${i}); do
		key=$(echo ${row} | awk 'BEGIN {FS="=" } {print $1}')
		value=$(echo ${row} | awk 'BEGIN {FS="=" } {print $2}')

		if [ ${key} == "oct" ]; then
			if [ -z ${opt_file} ]; then
				valid=false
				break
			fi
			run="${run} ${key} ${opt_file}"
		elif [ ${key} == "slo" ]; then
			if [ -z ${op_file} ]; then
				valid=false
				break
			fi
			run="${run} ${key} ${op_file}"
		elif [ ! ${key} == "version" ]; then
			if [ -z ${value} ]; then
				value=$(cat "${ASSETS_DIR}/executables/default.properties" | grep ${key} | awk 'BEGIN {FS="=" } {print $2}')
			fi
			run="${run} ${key} ${value}"
		fi
	done
	if [ ${valid} == false ]; then
		continue
	fi

	# run the algorithm and generate new output
	${run}

	# check for DICOM output and upload to xnat via curl
	algo_dcm="${ASSETS_DIR}/executables/${algo_name}_results.dcm"
	algo_txt="${ASSETS_DIR}/executables/${algo_name}_results.txt"

	cd ${WORK_DIR}

    TIME=$(date +%s)
    LOG="${LOG} ${TIME}"

	if [ -f ${algo_dcm} ]; then

		assessor_name="dcm_${algo_name}${algo_version}"
		assessor_url="${host}/REST/projects/${project}/subjects/${subject}/experiments/${session}"

		# check if assessor already exists
		curl ${XNAT_CACERT_FILE} -u ${user}:${pwd} "${assessor_url}/assessors?format=csv" > "assessors"
		existing_assessor=$(cat "assessors" | grep ${assessor_name})

		rm assessors

		if [[ -z ${existing_assessor} ]]; then
			# create new assessor
			curl ${XNAT_CACERT_FILE} -X PUT -u $user:$pwd "${assessor_url}/assessors/${assessor_name}?xsiType=xnat:imageAssessorData"
		else
			# if assessor already exists delete all files stored in assessor
			curl ${XNAT_CACERT_FILE} -u ${user}:${pwd} "${assessor_url}/assessors/${assessor_name}/files?format=csv" > "files"
			sed 1d "files" > "${assessor_name}.info"
			rm "files"

			for row in $(cat "${assessor_name}.info"); do
				file_to_delete=$(echo ${row} | awk 'BEGIN {FS="," } {print $3}' | sed 's/"//; s/"//')
				curl ${XNAT_CACERT_FILE} -X DELETE -u ${user}:${pwd} "${host}${file_to_delete}"
			done
		fi

		# upload file to assessor
		assessor_file_url="${host}/REST/projects/${project}/subjects/${subject}/experiments/${session}/assessors/${assessor_name}/resources/DICOM/files/${algo_name}_results.dcm"
		curl ${XNAT_CACERT_FILE} -X PUT -u ${user}:${pwd} "${assessor_file_url}?format=DICOM&content=T1_RAW&inbody=true" --data-binary @"${algo_dcm}"

	fi

	if [ -f ${algo_txt} ]; then

		for row in $(cat "${algo_txt}"); do
            key=$(echo ${row} | awk 'BEGIN {FS="=" } {print $1}')
            value=$(echo ${row} | awk 'BEGIN {FS="=" } {print $2}')
            type="qmroct:keyQualityIndicator"

            #Using printf to validate float value. If value is no valid float, the error message will be written into variable error. Otherwise it will be empty.
	        error=$( { printf "%.8f\n" ${value} > /dev/null; } 2>&1 )

            if [ -z ${error} ]; then
                value=$(printf "%.8f\n" ${value} | sed 's/\./%2E/')
                type="${type}Float"
            fi

            # upload command
            curl ${XNAT_CACERT_FILE} -X PUT -u ${user}:${pwd} "${host}/REST/projects/${project}/subjects/${subject}/experiments/${session}/assessors/${key}${algo_version}?${type}/value=${value}&${type}/name=${key}&${type}/algorithm=${algo_name}&${type}/version=${algo_version}"
        done
	fi

done

echo "OUTPUTMARKER ${LOG} OUTPUTMARKER"

cd
rm -r ${WORK_DIR}

exit 0