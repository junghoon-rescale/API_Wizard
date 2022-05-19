import requests
import json
import sys
import time
import csv


# Making a job including the License Queueing Feature with hpcdomains license
def make_job_hpc(apibaseurl, token, inputfile_name, inputfile_id, jobname, lowpriority, software, version,
             starccm_license, usf_hpcdomains, nslots_basic, coretype, ncores, walltime, project_code):
    makejob_url = apibaseurl + '/api/v2/jobs/'
    simname = inputfile_name.split(".")[0]
    if (inputfile_id != None):
        makejob = requests.post(
            makejob_url,
            headers={'Authorization': token},
            json={
                'isLowPriority': lowpriority,
                'name': jobname,
                'jobanalyses': [
                    {
                        'envVars': {
#                            'LM_PROJECT': lm_project,
                            'CDLMD_LICENSE_FILE': starccm_license,
                        },
                        'useRescaleLicense': 'false',
                        'onDemandLicenseSeller': '',
                        'userDefinedLicenseSettings': {
                            'featureSets': [
                                {
                                    'name': 'USER_SPECIFIED',
                                        'features': [
                                                {
                                                'name': 'hpcdomains',
                                                'count': usf_hpcdomains,
                                                },
                                                {
                                                'name': 'ccmpsuite',
                                                'count': '1',
                                                }
                                            ]
                                }
                            ]
                        },
                        'command': 'starccm+ -rsh ssh -np $RESCALE_CORES_PER_SLOT -machinefile $HOME/machinefile ' +
                                   '-batch autorun.java -load ' + simname + '.sim' + '\n' +
                                   'zip -r ' + jobname + '.zip *' + '\n' +
                                   'find . -name **.zip" -prune -o -name "*.log" -prune -o -exec rm -rf {} \;',
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


# Making a job with PowerSession license(In case of PowerSession license, License Queueing is pre-defined by platform)
def make_job_power(apibaseurl, token, inputfile_name, inputfile_id, jobname, lowpriority, software, version,
             starccm_license, nslots_basic, coretype, ncores, walltime, project_code):
    makejob_url = apibaseurl + '/api/v2/jobs/'
    simname = inputfile_name.split(".")[0]
    if (inputfile_id != None):
        makejob = requests.post(
            makejob_url,
            headers={'Authorization': token},
            json={
                'isLowPriority': lowpriority,
                'name': jobname,
                'jobanalyses': [
                    {
                        'envVars': {
#                            'LM_PROJECT': lm_project,
                            'CDLMD_LICENSE_FILE': starccm_license,
                        },
                        'useRescaleLicense': 'false',
                        'onDemandLicenseSeller': '',
                        # 'userDefinedLicenseSettings': {
                        #     'featureSets': [
                        #         {
                        #             'name': 'USER_SPECIFIED',
                        #                 'features': [
                        #                         {
                        #                         'name': 'hpcdomains',
                        #                         'count': usf_hpcdomains,
                        #                         },
                        #                         {
                        #                         'name': 'ccmpsuite',
                        #                         'count': '1',
                        #                         }
                        #                     ]
                        #         }
                        #     ]
                        # },
                        'command': 'starccm+ power -np $RESCALE_CORES_PER_SLOT -batch autorun.java ' +
                                   '-load ' + simname + '.sim' + '\n' +
                                   'zip -r ' + jobname + '.zip *' + '\n' +
                                   'find . -name **.zip" -prune -o -name "*.log" -prune -o -exec rm -rf {} \;',
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
#작업 제출 이후 7분이 경과하면 2분 간격으로 작업 현황을 확인하는 함수
# def monitoring_job(apibaseurl, token, job_id):
#     monitorjob_url = apibaseurl + '/api/v2/jobs/' + job_id + '/statuses/'
#     prev_status_count = 0
#     current_status_count = 0
#     job_completed = False
#     while job_completed == False:
#         monitorjob = requests.get(
#             monitorjob_url,
#             headers={'Authorization': token},
#         )
#         monitorjob_dict = json.loads(monitorjob.text)
#         current_status_count = monitorjob_dict['count']
#         if (current_status_count != prev_status_count):
#             job_status = monitorjob_dict['results']
#             print('The status of job ' + job_id + ' : ' + job_status[0]['status'])
#             #   필요 시 120을 더 큰 값으로 설정
#             time.sleep(120)
#             if (job_status[0]['status'] == 'Completed'):
#                 job_completed = True
#                 break
#     prev_status_count = current_status_count