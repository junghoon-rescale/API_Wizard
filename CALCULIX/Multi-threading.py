import tkinter.messagebox as msgbox
from tkinter import *
from tkinter import filedialog
import os
import sys
import csv
import time
import requests
import json
import threading
import JOBcalculix
import FILEcalculix

######################################################################################
######## This code is for making a GUI-based Rescale API Wizard on Windows OS ########
######################################################################################

root = Tk()
root.title("Rescale API Wizard for CalculiX")
root.geometry("1200x600")

# If you want to make a executable file through pyinstaller, cacert should be located in the same directory
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


## Write a job info csv file for monitoring the status
def writeinitfile():
    global csvfile
    csvfile = cwd + "\\Job_Summary.csv"
    column_names = [
        ['ID', 'NAME', 'SUBMIT_DATE', 'STATUS'],
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


## Getting a api settings from apiconfig
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


## Define the File Frame
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
    # After cleaning the information of input file, the color of button will get back to original
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
    inputfile_id = FILEcalculix.upload_inputfile(apibaseurl, token, inputfile)
    print('The file ID is ' + inputfile_id)
    # After finishing the upload a input file, the color of button will be changed as rescale blue
    btn_upload.configure(bg="#3399BB", fg="white")


btn_upload = Button(file_frame, text="Upload file", padx=5, pady=5, width=10, command=upload_file)
btn_upload.pack(side="left", padx=5, pady=5)

list_frame = LabelFrame(file_frame, text="Selected input file")
list_frame.pack(fill="both", padx=5, pady=5)

list_file = Listbox(list_frame, selectmode="extended", height=1)
list_file.pack(side="left", fill="both", expand=True, padx=5, pady=5)


root.resizable(False, False)
root.mainloop()
