# API_Wizard
API_Wizard is GUI-based launcher for helping to use of Rescale API

# Prerequisites
Install the Rescale-CLI and set up the apiconfig file
Install the Python 3.8(with requests, pyinstaller package)

# Included features
Users can make&manage a jobs through GUI(No need to log in to web-browser)
The license queueing feature could be enabled automatically

# How to use the program
  1. Add file: Select your input file to upload(*.zip) a) Upload file: Upload the selected input file b) Remove file: Remove the information of input file(If you make a mistake to select the input file)
  2. Open folder: Select the path where the result files will be saved(Generally, this is same folder where the input file is located)
  3. Job Settings: Define a setting values of job a) Input the job name in the user input region b) Select a version of ANSYS Fluent c) Select a coretype configuration(Coretype:Number of Cores) d) Select a license feature of ANSYS Fluent e) Select a project f) Submit the job by clicking the Submit button g) Remove the values by clicking the Clear button
  4. Job Monitoring: Monitor a jobs which are running and completed
    a) You can check the status of jobs by clicking the Status update button
    b) You can see a list of running jobs in the In-Progress field including the status(Queueing/Pending/Validating/Executing) : You can download a process_output.log during the job is running by clicking the specific job in the In-Progress field
    c) You can see a list of completed jobs in Completed field : You can download a results of job after the job is finished by clicking the specific job in the Completed field

# Execution method
  You can run the Python script directly(Launcher_fluent.py) using VS Code or PyCharm
  You can run the executable which could be made using PyInstaller package

# Reference
  User guide(For now, Korean only): https://docs.google.com/presentation/d/1Gjxasp8udsrodzsK74-JSYt5NXqsImOWDuJAMUFBOHM/edit?usp=sharing
