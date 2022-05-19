import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
from tkinter import *
from tkinter import filedialog
import os
import sys
import csv
import time
import requests
import json
import JOBstarccmp
import FILEstarccmp

root = Tk()
root.title("Rescale API Wizard for STAR-CCM+")
root.geometry("1200x600")

os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.path.dirname(sys.argv[0]), 'cacert.pem')
# Define a variables for using the API
global apibaseurl
global apikey
global token
global cwd
apibaseurl = ""
apikey = ""
token = ""
cwd = os.getcwd()


# Write a job info csv file for monitoring the status
def writeinitfile():
    global csvfile
    csvfile = cwd + "\\Job_Summary.csv"
    column_names = [
        ['ID', 'NAME', 'SUBMIT_DATE', 'STATUS'],
    ]
    if (not (os.path.exists(csvfile))):
        f = open(csvfile, 'w', newline='')
        writer = csv.writer(f)
        writer.writerows(column_names)
        f.close()
    else:
        f = open(csvfile, 'r')
        reader = csv.reader(f)
        for row in reader:
            print(row)
        f.close()


writeinitfile()


# Getting a api settings from apiconfig
homepath = os.path.expanduser("~")
setting_file = homepath + "\\.config\\rescale\\apiconfig"
try:
    f = open(setting_file, 'r', encoding='UTF8')
    lines = f.readlines()
    f.close()
except FileNotFoundError as e:
    print(e)
    sys.exit(1)

apibaseurl = lines[1].split('=')[1].rstrip('\n').lstrip().replace("'", "")
apikey = lines[2].split('=')[1].rstrip('\n').lstrip().replace("'", "")
token = "Token " + apikey


# 1 - File Frame
def add_file():
    list_file.delete(0, END)
    files = filedialog.askopenfilenames(title="Select a input file",
                                        filetypes=(("ZIP file", "*.zip"), ("All files", "*.*")),
                                        initialdir="C:/")
    if files =="":
        msgbox.showwarning("Warning", "You should add a input file")
    else:
        global inputfilefull
        for file in files:
            list_file.insert(END, file)
            inputfilefull = file
        btn_upload.configure(bg="#f0f0f0", fg="black")


def del_file():
    # for index in reversed(list_file.curselection()):
    #     list_file.delete(index)
    list_file.delete(0, END)
    print("Remove the selected input file")
    btn_upload.configure(bg="#f0f0f0", fg="black")


file_frame = LabelFrame(root, text="Input file")
file_frame.pack(side="top", fill="x", padx=5, pady=5)

btn_add_file = Button(file_frame, text="Add file", padx=5, pady=5, width=12, command=add_file)
btn_add_file.pack(side="left", padx=5, pady=5)

btn_del_file = Button(file_frame, text="Remove file", padx=5, pady=5, width=12, command=del_file)
btn_del_file.pack(side="left", padx=5, pady=5)


def upload_file():
    global inputfile_name
    global inputfile_id
    inputfile = inputfilefull.replace("/", "\\")
    inputfile_name = inputfile.split("\\")[-1]
    inputfile_id = FILEstarccmp.upload_inputfile(apibaseurl, token, inputfile)
    print('The file ID is ' + inputfile_id)
    btn_upload.configure(bg="#3399BB", fg="white")


btn_upload = Button(file_frame, text="Upload file", padx=5, pady=5, width=10, command=upload_file)
btn_upload.pack(side="left", padx=5, pady=5)

list_frame = LabelFrame(file_frame, text="Selected input file")
list_frame.pack(fill="both", padx=5, pady=5)

list_file = Listbox(list_frame, selectmode="extended", height=1)
list_file.pack(side="left", fill="both", expand=True, padx=5, pady=5)

# 2 - Save Path Frame
path_frame = LabelFrame(root, text="Save path")
path_frame.pack(side="top", fill="x", padx=5, pady=5, ipady=5)

txt_dest_path = Entry(path_frame)
txt_dest_path.pack(side="left", fill="x", expand=True, ipady=4, padx=5, pady=5)


def browse_dest_path():
    folder_selected = filedialog.askdirectory()
    if folder_selected is None:
        return
    txt_dest_path.delete(0, END)
    txt_dest_path.insert(0, folder_selected)
    global save_path
    save_path = str(folder_selected)


btn_dest_path = Button(path_frame, text="Open folder", command=browse_dest_path)
btn_dest_path.pack(side="right", padx=5, pady=5)

# 3 - Job Submission Frame
job_frame = LabelFrame(root, text="Job Settings")
job_frame.pack(side="top", fill="x", expand=True, padx=5, pady=30, ipadx=5, ipady=40)

job_name = Entry(job_frame, width=14)
job_name.pack(side="left", fill="x", padx=5, pady=5, expand=True)
job_name.insert(0, "Input the job name")

# enable_ad = ["yes", "no"]
# autodown = ttk.Combobox(job_frame, width=18, height=1, value=enable_ad, state="readonly")
# autodown.current(0)
# autodown.set("Automatic Download")
# autodown.pack(side="left", padx=5, pady=5)

list_version = ["16.06.010", "16.06.010-r8", "16.04.012", "16.04.012-r8", "16.02.009", "16.02.009-r8",
                "15.06.008", "15.06.008-r8", "15.04.010", "15.04.010-r8", "15.02.009", "15.02.009-r8",
                "14.06.013", "14.06.013-r8", "14.04.013", "14.04.013-r8", "14.02.012", "14.02.012-r8"]
swversion = ttk.Combobox(job_frame, width=12, height=3, value=list_version, state="readonly")
swversion.current(0)
swversion.set("Version")
swversion.pack(side="left", padx=5, pady=5)

list_config = ["emerald:18", "emerald:36", "calcite:16", "calcite:24", "calcite:32",
               "chromium:16", "chromium:24", "chromium:32",
               "carbon:44", "carbon:88", "carbon:176", "carbon:264", "carbon:352", "carbon:440", "carbon:528",
               "jasper:60", "jasper:120", "jasper:240", "jasper:360", "jasper:480", "jasper:600", "jasper:720",
               "peridot:44", "peridot:88","peridot:176","peridot:264","peridot:352","peridot:440","peridot:528",]
hwconfig = ttk.Combobox(job_frame, width=14, height=3, value=list_config, state="readonly")
hwconfig.set("Coretype config")
hwconfig.pack(side="left", padx=5, pady=5)

list_license_type = ["hpcdomains", "PowerSession"]
license_type = ttk.Combobox(job_frame, width=12, height=3, value=list_license_type, state="readonly")
license_type.current(0)
license_type.set("License type")
license_type.pack(side="left", padx=5, pady=5)

list_projects = ["Project A", "Project B", "Project C", "Project D", "Project E"]
list_projectcode = ["a", "b", "c", "d", "e"]
dict_projects = {name: value for name, value in zip(list_projects, list_projectcode)}
projects = ttk.Combobox(job_frame, width=14, height=3, value=list_projects, state="readonly")
projects.current(0)
projects.set("Project")
projects.pack(side="left", padx=5, pady=5)


def submit_job():
    # Getting a job settings from GUI environment
    global jobname
    global job_id
    global adflag
    global license_type
    global submit_date
    submit_date = ""
    jobname = str(job_name.get())
    software = "cd_adapco_star_ccm"
    version = str(swversion.get())
    licensetype = str(license_type.get())
    hwsetting = str(hwconfig.get())
    coretype = hwsetting.split(":")[0]
    ncores = hwsetting.split(":")[1]
    walltime = "72"
    lowpriority = "true"
    nslots_basic = "1"
    starccm_license = "PORT@HOSTNAME"
    lm_project = ""
    project_code = dict_projects.get(str(projects.get()))
    print(project_code)
    # adflag = str(autodown.get())
    if licensetype == 'hpcdomains':
        usf_hpcdomains = int(ncores) - 1
        job_id = JOBstarccmp.make_job_hpc(apibaseurl, token, inputfile_name, inputfile_id, jobname, lowpriority,
                                         software,version, starccm_license, usf_hpcdomains, nslots_basic,
                                         coretype, ncores, walltime, project_code)
    else:
        job_id = JOBstarccmp.make_job_power(apibaseurl, token, inputfile_name, inputfile_id, jobname, lowpriority,
                                                 software, version, starccm_license, nslots_basic,
                                                 coretype, ncores, walltime, project_code)
    print('The job ID is ' + job_id)
    JOBstarccmp.submit_job(apibaseurl, token, job_id)
    submit_date = time.ctime(time.time())
    print('Submission date is ' + submit_date)
    JOBstarccmp.appenddata_job(csvfile, job_id, jobname, submit_date)
    btn_submit.configure(bg="#3399BB")


btn_submit = Button(job_frame, text="Submit", padx=5, pady=5, width=10, command=submit_job)
btn_submit.pack(side="left", padx=5, pady=5)

def clear_settings():
    list_file.delete(0, END)
    job_name.delete(0, END)
    job_name.insert(0, "Input the job name")
    # autodown.set("Automatic Download")
    swversion.set("Version")
    hwconfig.set("Coretype config")
    license_type.set("License type")
    projects.set("Project")
    btn_submit.configure(bg="#f0f0f0")


btn_clear = Button(job_frame, text="Clear", padx=5, pady=5, width=10, command=clear_settings)
btn_clear.pack(side="left", padx=5, pady=5)


# 4 - Job Monitoring Frame
job_monitor_frame = LabelFrame(root, text="Job Monitoring")
job_monitor_frame.pack(side="top", fill="x", padx=5, pady=5)


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
        job_line[i][3] = job_status

    global job_summary
    job_summary = [
        ['job_id', 'jobname'],
    ]
    global inprogress_job_temp
    global completed_job_temp
    inprogress_job_temp = []
    completed_job_temp = []
    f = open(csvfile, 'w' , newline='')
    writer = csv.writer(f)
    writer.writerows(job_line)
    f.close()
    for i in range(1, njobs):
        job_identity = job_line[i][0] + ":" + job_line[i][1]
        job_summary.append(job_identity)
        if job_line[i][3] == 'Completed':
            completed_job_identity = job_summary[i]
            completed_job_temp.append(completed_job_identity)
        elif job_line[i][3] != 'Completed':
            inprogress_job_identity = job_summary[i] + ":" + job_line[i][3]
            inprogress_job_temp.append(inprogress_job_identity)


job_inprogress_frame = LabelFrame(job_monitor_frame, text="In-Progress")
job_inprogress_frame.pack(side="left", fill="x", padx=5, pady=5)


def changeinprogressjoblist():
    if inprogress_job_temp != "":
        job_inprogress_list["value"] = inprogress_job_temp
    else:
        job_inprogress_list["value"] = "In-Progress"


def selectedinprogressjob(event):
    global selected_inprogress_job_summary
    selected_inprogress_job_summary = event.widget.get()


inprogress_job = ["In-Progress"]
job_inprogress_list = ttk.Combobox(job_inprogress_frame, width=60, height=10, value=inprogress_job,
                                   state="readonly", postcommand=changeinprogressjoblist)
job_inprogress_list.bind("<<ComboboxSelected>>", selectedinprogressjob)
job_inprogress_list.pack(side="left", padx=5, pady=5)


job_completed_frame = LabelFrame(job_monitor_frame, text="Completed")
job_completed_frame.pack(side="left", fill="x", padx=5, pady=5)


def changecompletedjoblist():
    job_completed_list["value"] = completed_job_temp


def selectedcompletedjob(event):
    global selected_completed_job_summary
    selected_completed_job_summary = event.widget.get()


completed_job = ["Completed"]
job_completed_list = ttk.Combobox(job_completed_frame, width=60, height=10, value=completed_job,
                                   state="readonly", postcommand=changecompletedjoblist)
job_completed_list.bind("<<ComboboxSelected>>", selectedcompletedjob)
job_completed_list.pack(side="left", padx=5, pady=5)


def download_log():
    selected_inprogress_job = selected_inprogress_job_summary.split([":"][0])
    job_id = selected_inprogress_job[0]
    FILEstarccmp.download_poutlog(save_path, job_id)


def download_job():
    selected_completed_job = selected_completed_job_summary.split([":"][0])
    job_id = selected_completed_job[0]
    jobname = selected_completed_job[1]
    FILEstarccmp.download_outputfile(apibaseurl, token, job_id, jobname, save_path)


btn_status = Button(job_monitor_frame, text="Status update", padx=5, pady=5, width=24, command=status_job)
btn_status.pack(side="top", padx=5, pady=5)

btn_poutlog = Button(job_monitor_frame, text="Download process_output.log", padx=5, pady=5, width=24,
                   command=download_log)
btn_poutlog.pack(side="top", padx=5, pady=5)

btn_download = Button(job_monitor_frame, text="Download results", padx=5, pady=5, width=24, command=download_job)
btn_download.pack(side="top", padx=5, pady=5)

root.resizable(False, False)
root.mainloop()
