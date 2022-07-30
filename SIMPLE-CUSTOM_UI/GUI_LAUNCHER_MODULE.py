import requests
import json
import sys
import csv
import os

# Function: create a csv file for logging the job information
def writeinitfile(csvfile):
    column_names = [
        ['ID', 'STATUS'],
    ]
    # If the job info csv file is not existing, it would be made at current directory
    if (not (os.path.exists(csvfile))):
        f = open(csvfile, 'w', newline='')
        writer = csv.writer(f)
        writer.writerows(column_names)
        f.close()
    # If the job info csv file is already existing, it would be read a job info from csv file
    else:
        f = open(csvfile, 'r')
        reader = csv.reader(f)
        for row in reader:
            print(row)
        f.close()


# Function: make a OpenFOAM job through OpenFOAM+
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


# Function: Submit the created job
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

# Function: Add a new job information to Job_Summary.csv
def appenddata_job(csvfile, job_id):
    data = [
        [job_id, ""],
    ]
    f = open(csvfile, 'a', newline='')
    writer = csv.writer(f)
    writer.writerows(data)
    f.close()

# Function: Upload the inputfile
def upload_inputfile(apibaseurl, token, inputfile):
    upload_url = apibaseurl + '/api/v2/files/contents/'
    try:
        upload_file = requests.post(
            upload_url,
            data=None,
            headers={'Authorization': token},
            files={'file': open(inputfile, 'rb')},
        )
        if (upload_file.status_code == 201):
            print('Uploading the input file is done')
            upload_file_dict = json.loads(upload_file.text)
            inputfile_id = upload_file_dict['id']
        else:
            print('Uploading the input file is failed')
            exit(1)
    except FileNotFoundError as e:
        print(e)
        exit(1)
    return inputfile_id

# Function: Download a result(Filtering only *.zip file)
def download_results(apibaseurl, token, job_id, save_path):
    postjob_url = apibaseurl + '/api/v2/jobs/' + job_id + '/files/'
    current_page = 1
    last_page = False
    while (not (last_page)):
        postoutput_files = requests.get(
            postjob_url,
            headers={'Authorization': token},
            params={'page': current_page},
        )
        postoutput_files_dict = json.loads(postoutput_files.text)
        #    print(postoutput_files_dict)
        postcount = postoutput_files_dict['count']
        #   Svae the information of output file up to 10
        if current_page == 1:
            postoutputfileid = [0 for i in range(postcount)]
            postoutputfilename = [0 for i in range(postcount)]
            postoutputfileurl = [0 for i in range(postcount)]
            if postcount <= 10:
                for i in range(0, postcount):
                    postoutputfileid[i] = postoutput_files_dict['results'][i]['id']
                    postoutputfilename[i] = postoutput_files_dict['results'][i]['name']
                    postoutputfileurl[i] = postoutput_files_dict['results'][i]['downloadUrl']
            else:
                for i in range(0, 10):
                    postoutputfileid[i] = postoutput_files_dict['results'][i]['id']
                    postoutputfilename[i] = postoutput_files_dict['results'][i]['name']
                    postoutputfileurl[i] = postoutput_files_dict['results'][i]['downloadUrl']
        elif postcount > 10 and current_page == 1:
            for i in range(0, 10):
                postoutputfileid[i] = postoutput_files_dict['results'][i]['id']
                postoutputfilename[i] = postoutput_files_dict['results'][i]['name']
                postoutputfileurl[i] = postoutput_files_dict['results'][i]['downloadUrl']
        #   If the number of output file is above 10, modifying the index information for saving
        elif postcount < current_page * 10 and postcount > 10:
            indexup = (current_page - 1) * 10
            uplimit = postcount % indexup
            for i in range(0, uplimit):
                postoutputfileid[i + indexup] = postoutput_files_dict['results'][i]['id']
                postoutputfilename[i + indexup] = postoutput_files_dict['results'][i]['name']
                postoutputfileurl[i] = postoutput_files_dict['results'][i]['downloadUrl']
        else:
            indexup = (current_page - 1) * 10
            for i in range(0, 10):
                postoutputfileid[i + indexup] = postoutput_files_dict['results'][i]['id']
                postoutputfilename[i + indexup] = postoutput_files_dict['results'][i]['name']
                postoutputfileurl[i] = postoutput_files_dict['results'][i]['downloadUrl']
        #   If the number of output file is above 10, it will be repeated up to the last page
        if (postoutput_files_dict['next'] == None):
            last_page = True
        else:
            current_page += 1
    #   Create a dictionary including the name of file and id
    output_files_info = dict(zip(postoutputfilename, postoutputfileid))
    #   In the list of file, search a output files and save the key and value
    outputfileextension = ['.zip']
    outputfileidlist = []
    for i in outputfileextension:
        search = i
        for j in output_files_info.keys():
            if search in j:
                outputfileidlist.append(output_files_info.get(j))
    #   Check the id of '*.zip' file
    processingfile_id = outputfileidlist[0]
    for key, value in output_files_info.items():
        if value == processingfile_id:
            processingfile_name = key
    #   Check the file name of previous step
    save_folder = os.path.join(save_path, job_id)
    print(save_folder)
    if (not (os.path.exists(save_folder))):
        os.makedirs(save_folder)
    os.chdir(save_folder)
    #   If there is no existing folder, make the folder
    #   Download the file
    outputfile_url = apibaseurl + '/api/v2/files/' + processingfile_id + '/contents/'
    response = requests.get(
        outputfile_url,
        headers={'Authorization': token},
    )
    with open(processingfile_name, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            fd.write(chunk)
	print("The download of job ID: " + job_id + "  is done")
