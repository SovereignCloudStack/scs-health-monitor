# Environment setup 

1) Create [venv](https://docs.python.org/3/library/venv.html)
2) In this repository (under main directory) you have to create two files that will be referenced by `env.yaml` and `clouds.yaml`
3) env.yaml:
```
   OS_AUTH_TYPE: ""
   OS_AUTH_URL: ""
   OS_IDENTITY_API_VERSION: ""
   OS_REGION_NAME: ""
   OS_INTERFACE: ""
   OS_APPLICATION_CREDENTIAL_ID: ""
   OS_APPLICATION_CREDENTIAL_SECRET: ""
   OS_PROJECT_NAME: ""
   OS_USER_DOMAIN_NAME: ""
   OS_PROJECT_DOMAIN_NAME: ""

   ```
4) clouds.yaml:
```
clouds:
  gx:
    region_name:
    auth_type:
    auth_url:
    identity_api_version:
    interface:
    application_credential_id:
    application_credential_secret:
```

   
# GIT workflow 
Issues should be created [here](https://github.com/SovereignCloudStack/issues/labels/SCS-VP12). The issue should be clearly defined and also have an asignee and label "SCS-VP12" defined.

Adding fixes to the project:
1) Create branch for issue `git checkout -b SPACECAT-<issue_number>-<issue_name>`.
2) Add the changes made `git add -u` or `git add <file_name>`.
3) Commit the changes using `git commit -s -m "message"`.
   - The "-s" flag is important, the commit won't go through otherwise
4) To push the current branch and the changes and set the remote as upstream, use `git push --set-upstream origin SPACECAT-<issue_number>-<issue_name>`.
   - Alternatively push the changes if the branch already exists in the remote repository.
5) After work is done, create a pull request for the branch.
6) Ask another team member to review the changes, when he approves the changes, merge the chages into main branch.

# Python

## Command cheatsheet
``` bash
# create python virtual environment
python3 -m venv env/<environment_name>

# activate the python virtual environment in windows command prompt
env/<environment_name>/Scripts/activate   

# activate the python virtual environment in Unix or MacOS
source env/<environment_name>/bin/activate

# install all the python dependencies
python -m pip install -r requirements.txt 
```