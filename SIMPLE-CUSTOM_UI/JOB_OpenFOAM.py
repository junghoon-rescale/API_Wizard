import requests
import json
import sys
import csv


# Function: make job
def make_job(apibaseurl, token, inputfile_id):
    makejob_url = apibaseurl + '/api/v2/jobs/'
    if (inputfile_id != None):
        makejob = requests.post(
            makejob_url,
            headers={'Authorization': token},
            json={
                'isLowPriority': 'false',
                'name': 'Job from Custom UI',
                'jobanalyses': [
                    {
                        'envVars': {},
                        'useRescaleLicense': 'false',
                        'onDemandLicenseSeller': '',
                        'userDefinedLicenseSettings': {
                            'featureSets': []
                        },
                        'command': 'cd airfoil2D' + '\n' +
                                    './Allrun' + '\n' +
                                   'zip -r outputs.zip * -x "*tmp"' + '\n' +
                                   'find . -name "*.zip" -prune -o -name "*.log" -prune -o -exec rm -rf {} \;',
                        'analysis': {
                            'code': 'openfoam_plus',
                            'version': 'v1706+-intelmpi'
                        },
                        'hardware': {
                            'coresPerSlot': '4',
                            'walltime': '24',
                            'slots': '1',
                            'coreType': 'emerald',
                        },
                        'inputFiles': [
                            {
                                'id': inputfile_id
                            },
                        ],
                    },
                ],
                'projectId': 'BKuia',
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


def appenddata_job(csvfile, job_id):
    data = [
        [job_id, ""],
    ]
    f = open(csvfile, 'a', newline='')
    writer = csv.writer(f)
    writer.writerows(data)
    f.close()
