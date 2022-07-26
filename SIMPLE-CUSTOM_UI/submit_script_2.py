#This is a sample script for submitting jobs on the Rescale cluster using REST API calls
#The projectId is "gxzXS"

import requests


class RescaleJob:

  def __init__(self, token):
    self.token = token
    

  def uploadFile(self):
    print("\nUploading the input file to the Rescale cluster\n")
    uploadFile = requests.post(
      'https://platform.rescale.com/api/v2/files/contents/',
      data=None,
      files={'file': open('airfoil2D.zip','rb')},
      headers={'Authorization': 'Token '+self.token} 
    )

    #This is the data returned back by the REST API
    uploadFile_json = uploadFile.json()
    print(uploadFile_json)
    #This is the File Id necessary to creating a new job
    print('\nFileID: '+ uploadFile_json["id"])

    return uploadFile_json["id"] 


  def createNewJob(self, fileID):
    #All the information required to setup a new simulation is included in the json array
    #The analysis and core information has been gathered by separate cURL API calls shown below
    #This data can be formatted using - https://jsonlint.com/
    #curl -H "Authorization: Token 37bda0da4f921498147c6c9f1e66002c3c8d8a69" "https://platform.rescale.com/api/v2/coretypes/?page_size=50&?page=1" >cores.txt
    #curl -H "Authorization: Token 37bda0da4f921498147c6c9f1e66002c3c8d8a69" "https://platform.rescale.com/api/v2/analyses/?page_size=100&?page=1" >analyses_1.txt

    #After the inital job submission through the ScaleX Web Interface, the details can be obtained by the below REST call.
    #The command, code, version etc can be confirmed using this information
    #curl -H "Authorization: Token 37bda0da4f921498147c6c9f1e66002c3c8d8a69" https://platform.rescale.com/api/v2/jobs/RyZtTc/
    print("\nCreating a new job!\n")
    newJob = requests.post(
      'https://platform.rescale.com/api/v2/jobs/',
      headers={'Content-Type': 'application/json',
              'Authorization': 'Token '+self.token},
      json={
          'name': 'Example Job_18',
          'jobanalyses': [
              {
                  'analysis': {
                      'code': 'openfoam_plus',
                      'version': 'v1706+-intelmpi'
                  },
                  'useRescaleLicense': False, 
                  'command': "cd airfoil2D\n./Allrun",
                  'hardware': {
                      'slots': 1, 
                      'coreType': 'emerald',
                      'coresPerSlot': 1
                  },
                  'inputFiles': [ 
                      { 
                        'id': fileID
                      }
                  ]
              }
          ],
          "projectId": "gxzXS",
      }
    )

    newJob_json = newJob.json()
    print(newJob_json)
    #This is the Job Id which is required for job submission and monitoring
    var_jobID = newJob_json["id"] 
    print("\nJobID: "+var_jobID)

    return var_jobID


  def submitJob(self, jobID):
    print('\nSubmitting the job: '+jobID)
    submit_job = requests.post(
      'https://platform.rescale.com/api/v2/jobs/'+jobID+'/submit/',
      headers={'Authorization': 'Token '+self.token} 
    )
    #print(submit_job.content) #no return value for submit job


  def monitorJob(self, jobID):
    print('\nmonitoring the job: '+jobID)
    job_status = requests.get(
      'https://platform.rescale.com/api/v2/jobs/'+jobID+'/statuses/',
      headers={'Authorization': 'Token '+self.token} 
    )
    print(job_status.content)


if __name__ == '__main__':

  print("\nWelcome! Submit a job on the Rescale platform..!\n")

  # The token should be saved as environment or system variable and should not be visible in the code
  # on Windows - set RESCALE_API_KEY=37bda0da4f921498147c6c9f1e66002c3c8d8a69
  # echo %RESCALE_API_KEY%
  #For simplicity, the code is used as a variable here
  var_token = '37bda0da4f921498147c6c9f1e66002c3c8d8a69' 

  newSimulation = RescaleJob(var_token)
  uploadFileId = newSimulation.uploadFile()
  jobID = newSimulation.createNewJob(uploadFileId)
  newSimulation.submitJob(jobID)
  newSimulation.monitorJob(jobID)

  print("\nSimulation Complete..!\n")

  #sys.exit(main())  # next section explains the use of sys.exit




"""
Other API calls that were useful for writing this script
#-------------------------------------------------------
print('List all available core types')
coreTypes = requests.get(
  'https://platform.rescale.com/api/v2/coretypes/',
  headers={'Authorization': 'Token '+var_token}
)
print(coreTypes.json())
#-------------------------------------------------------
print('List all available softwares for analysis')
analyses = requests.get(
  'https://platform.rescale.com/api/v2/analyses/',
  headers={'Authorization': 'Token '+var_token}
)
print(analyses.json())
#-------------------------------------------------------
print('List all files')
allFiles = requests.get(
  'https://platform.rescale.com/api/v2/files/',
  headers={'Authorization': 'Token '+var_token}
)
print(allFiles.json())
#-------------------------------------------------------
print('Get Pricing information')
price = requests.get('https://platform.rescale.com/api/v2/billing/computeprices/',
  headers={'Authorization': 'Token '+var_token}
)
print(price.text)
print(price.json())
print(price.headers)
#-------------------------------------------------------
print('Delete a job #kZydXb')
requests.delete(
    'https://platform.rescale.com/api/v2/jobs/kZydXb/',
    headers={'Authorization': 'Token '+var_token}
)
#-------------------------------------------------------
"""