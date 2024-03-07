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
env\<environment_name>\Scripts\activate   

# activate the python virtual environment in Unix or MacOS
source env/<environment_name>/bin/activate

# install all the python dependencies
python -m pip install -r requirements.txt 
```