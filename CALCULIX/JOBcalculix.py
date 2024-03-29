import requests
import json
import sys
import time
import csv


# Function: make job
def make_job(apibaseurl, token, inputfile_name, inputfile_id, jobname, lowpriority, software, version,
             nslots_basic, coretype, ncores, walltime, project_code):
    makejob_url = apibaseurl + '/api/v2/jobs/'
    inpname = inputfile_name.split(".")[0]
    if (inputfile_id != None):
        makejob = requests.post(
            makejob_url,
            headers={'Authorization': token},
            json={
                'isLowPriority': lowpriority,
                'name': jobname,
                'jobanalyses': [
                    {
                        'envVars': {},
                        'useRescaleLicense': 'false',
                        'onDemandLicenseSeller': '',
                        'userDefinedLicenseSettings': {
                            'featureSets': []
                        },
                        'command': 'export OMP_NUM_THREADS=$RESCALE_CORES_PER_SLOT' + '\n' +
                                   'dos2unix' + ' ' + inpname + '.inp' + '\n' +
                                   'calculixMT' + ' ' + inpname + '\n' +
                                   'zip -r ' + jobname + '.zip * -x "*shared*" "*tmp"' + '\n' +
                                   'find . -name "*.zip" -prune -o -name "*.log" -prune -o -exec rm -rf {} \;',
                        'analysis': {
                            'code': software,
                            'version': version
                        },
                        'hardware': {
                            'coresPerSlot': ncores,
                            'walltime': walltime,
                            'slots': nslots_basic,
                            'coreType': coretype,
                        },
                        'inputFiles': [
                            {
                                'id': inputfile_id
                            },
                        ],
                    },
                ],
                'projectId': project_code,
            },
        )
        if (makejob.status_code != 201):
            print(makejob.text)
            print('Creating a job is failed')
            sys.exit(1)
        else:
            print('The job is created successfully')
    else:
        print('Unexpected error, please contact support')
    makejob_dict = json.loads(makejob.text)
    job_id = makejob_dict['id'].strip()
    return job_id


# 앞서 생성한 작업을 Submit
def submit_job(apibaseurl, token, job_id):
    submitjob_url = apibaseurl + '/api/v2/jobs/' + job_id + '/submit/'
    submitjob = requests.post(
        submitjob_url,
        headers={'Authorization': token},
    )
    if (submitjob.status_code == 200):
        print('The job ' + job_id + ' is submitted')
    else:
        error_code = submitjob.status_code
        print('Job submission is failed with error')


# Status update를 위하여 파일에 내용을 기입하는 함수
def timestamps_job():
    timestamps_raw = time.time()
    submit_date = time.ctime(timestamps_raw)


def appenddata_job(csvfile, job_id, jobname, submit_date):
    data = [
        [job_id, jobname, submit_date, ""],
    ]
    f = open(csvfile, 'a', newline='')
    writer = csv.writer(f)
    writer.writerows(data)
    f.close()
