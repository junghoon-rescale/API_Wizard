import requests
import json
import os

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


def download_poutlog(save_path, job_id):
    command_path = "cd " + save_path
    command_cli = "rescale-cli download-file -j" + " " + job_id + " " + "-f process_output.log"
    os.system("start cmd /c powershell.exe " + command_path + ";" + command_cli)


def download_outputfile(apibaseurl, token, job_id, jobname, save_path):
    postjob_url = apibaseurl + '/api/v2/jobs/' + job_id + '/files/'
    current_page = 1
    last_page = False
    current_dir = os.getcwd()
    while (not (last_page)):
        postoutput_files = requests.get(
            postjob_url,
            headers={'Authorization': token},
            params={'page': current_page},
        )
        postoutput_files_dict = json.loads(postoutput_files.text)
        #    print(postoutput_files_dict)
        postcount = postoutput_files_dict['count']
        #   10개까지의 Output file 정보를 목록으로 저장
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
        #   Output file의 수가 10개 이상일 경우 index 정보를 수정하여 목록으로 저장
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
        #   Output file의 수가 10개 이상일 경우 다음 10개의 정보 확인을 위하여 while 루프를 추가로 순환
        if (postoutput_files_dict['next'] == None):
            last_page = True
        else:
            current_page += 1
    #   전체 Output file들의 목록을 확인하면 while 루프 탈출
    #   Post-processing job에서 생성된 파일의 이름과 ID만 추출하여 새로운 Dictionary 생성
    output_files_info = dict(zip(postoutputfilename, postoutputfileid))
    #   파일 목록에서 결과 파일에 해당되는 항목을 검색하여 key 및 value 저장
    outputfileextension = ['.zip']
    outputfileidlist = []
    for i in outputfileextension:
        search = i
        for j in output_files_info.keys():
            if search in j:
                outputfileidlist.append(output_files_info.get(j))
    #   '.zip' 확장자를 가진 파일의 id 확인
    processingfile_id = outputfileidlist[0]
    for key, value in output_files_info.items():
        if value == processingfile_id:
            processingfile_name = key
    #   앞서 확인한 파일의 id로 파일 이름을 확인
    save_folder = os.path.join(save_path, jobname)
    print(save_folder)
    if (not (os.path.exists(save_folder))):
        os.makedirs(save_folder)
    os.chdir(save_folder)
    #   기존에 동일한 이름으로 생성된 폴더가 없을 경우 생성 후 이동
    # ++++Post-processing job의 결과 파일을 다운로드++++#
    outputfile_url = apibaseurl + '/api/v2/files/' + processingfile_id + '/contents/'
    response = requests.get(
        outputfile_url,
        headers={'Authorization': token},
    )
    with open(processingfile_name, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            fd.write(chunk)