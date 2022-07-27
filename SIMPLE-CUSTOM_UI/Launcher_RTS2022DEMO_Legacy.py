import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
from tkinter import *
from tkinter import filedialog
import os
import csv
import requests
import json
import JOB_OpenFOAM
import FILE_OpenFOAM


# If you want to make a executable file through pyinstaller, cacert should be located in the same directory
# os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.path.dirname(sys.argv[0]), 'cacert.pem')

# section 1.0
root = Tk()
root.title("Custom UI")
root.geometry("480x300")
#   Define a variables for using the API
global apibaseurl
global apikey
global token
global cwd
#   If necessary, change the apibaseurl
apibaseurl = "<Your API base(Prod)>"
#   You should use your api key
apikey = "<Your Personal API Key>"
token = "Token " + apikey
cwd = os.getcwd()


# section 1.1
#   Write a job info csv file for monitoring the status
def writeinitfile():
    global csvfile
    # If your OS is not windows, you need to change the "\\"
    csvfile = cwd + "\\Job_Summary.csv"
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
writeinitfile()


# section 1.2
#   Make a frame
file_frame = LabelFrame(root, width=45)
file_frame.pack(side="top", fill="x", padx=5, pady=5)
#   Define the add_file function
def add_file():
    list_file.delete(0, END)
    files = filedialog.askopenfilenames(title="Select a input file",
                                        filetypes=(("ZIP file", "*.zip"), ("All files", "*.*")),
                                        initialdir="C:/")
    if files =="":
        msgbox.showwarning("Warning", "You should add a input file")
    else:
        global inputfilefull
        global inputfile
        global save_path
        for file in files:
            list_file.insert(END, file)
            inputfilefull = file
            # If your OS is not windows, you need to change the "\\"
            inputfile = inputfilefull.replace("/", "\\")
            save_path = os.path.dirname(inputfile)
        btn_upload.configure(bg="#f0f0f0", fg="black")
#   Make a button for selecting the input file
btn_add_file = Button(file_frame, text="Select file", padx=5, pady=5, width=10, command=add_file)
btn_add_file.pack(side="left", padx=5, pady=5)
#   Define the upload_file function
def upload_file():
    global inputfile_id
    inputfile_id = FILE_OpenFOAM.upload_inputfile(apibaseurl, token, inputfile)
    print('The file ID is ' + inputfile_id)
    # After finishing the upload a input file, the color of button will be changed as rescale blue
    btn_upload.configure(bg="#3399BB", fg="white")
#   Make a button for uploading the input file
btn_upload = Button(file_frame, text="Upload file", padx=5, pady=5, width=10, command=upload_file)
btn_upload.pack(side="right", padx=5, pady=5)
#   Make a sub-frame
list_frame = LabelFrame(file_frame, text="Selected file", width=20)
list_frame.pack(side="top", fill="both", padx=5, pady=5)
#   Listbox for displaying the selected input file
list_file = Listbox(list_frame, selectmode="extended", height=1)
list_file.pack(side="left", fill="both", expand=True, padx=5, pady=5)


# section 2.0
#   Make a frame
job_frame = LabelFrame(root)
job_frame.pack(side="top", fill="x", padx=5, pady=5)
#   Define the job settings
def submit_job():
    # Getting a job settings from GUI environment
    job_id = JOB_OpenFOAM.make_job(apibaseurl, token, inputfile_id)
    print('The job ID is ' + job_id)
    JOB_OpenFOAM.submit_job(apibaseurl, token, job_id)
    print('The job ID ' + job_id + ' is submitted')
    JOB_OpenFOAM.appenddata_job(csvfile, job_id)
    # After job is submitted successfully, the color of button will be changed as rescale blue
    btn_submit.configure(bg="#3399BB")
#   Make a button for submitting the job
btn_submit = Button(job_frame, text="Job Submit", padx=5, pady=5, width=17, command=submit_job)
btn_submit.pack(side="left", padx=5, pady=5)


# section 3.0
# 4 - Job Monitoring Frame
job_monitor_frame = LabelFrame(root)
job_monitor_frame.pack(side="top", fill="both", padx=5, pady=5)


def status_job():
    # FILEgeneralcalculix.download_poutlog(save_path, job_id)
    global job_line
    global njobs
    job_line = []

    f = open(csvfile, "r")
    reader = csv.reader(f)
    for row in reader:
        job_line.append(row)
    f.close()

    njobs = len(job_line)
    for i in range(1, njobs):
        current_line = job_line[i][0]
        monitoring_url = apibaseurl + '/api/v2/jobs/' + current_line + '/statuses/'
        monitorjob = requests.get(
            monitoring_url,
            headers={'Authorization': token},
        )
        monitorjob_dict = json.loads(monitorjob.text)
        status_check = monitorjob_dict['results']
        job_status=status_check[0]['status']
        job_line[i][1] = job_status

    global job_summary
    job_summary = [
        ['job_id', 'job_status'],
    ]
    global job_status_temp
    job_status_temp = []
    f= open(csvfile, 'w', newline='')
    writer = csv.writer(f)
    writer.writerows(job_line)
    f.close()
    for i in range(1, njobs):
        job_identity = job_line[i][0] + ":" + job_line[i][1]
        job_summary.append(job_identity)
        job_status_temp.append(job_identity)


job_status_frame = LabelFrame(job_monitor_frame)
job_status_frame.pack(side="left", fill="x", padx=5, pady=5)


def changeinprogressjoblist():
    if job_status_temp != "":
        job_status_list["value"] = job_status_temp
    else:
        job_status_list["value"] = "No Data for now"


def selectedinprogressjob(event):
    global selected_job_summary
    selected_job_summary = event.widget.get()


status_of_job = ["Need to update the status"]
job_status_list = ttk.Combobox(job_status_frame, width=90, height=10, value=status_of_job,
                                   state="readonly", postcommand=changeinprogressjoblist)
job_status_list.bind("<<ComboboxSelected>>", selectedinprogressjob)
job_status_list.pack(side="left", padx=5, pady=5)

btn_status = Button(job_frame, text="Update Status", padx=10, pady=5, width=17, command=status_job)
btn_status.pack(side="left", padx=5, pady=5)


def download_job():
    selected_completed_job = selected_job_summary.split([":"][0])
    job_id = selected_completed_job[0]
    status = selected_completed_job[1]
    if status == 'Completed':
        FILE_OpenFOAM.download_results(apibaseurl, token, job_id, save_path)
    else:
        print("The job should be completed before you try to download it")


btn_download = Button(job_frame, text="Download Job", padx=5, pady=5, width=17, command=download_job)
btn_download.pack(side="left", padx=5, pady=5)


root.resizable(False, False)
root.mainloop()
