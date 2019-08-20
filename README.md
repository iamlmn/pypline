# pyplines Static Code Analysis 


## Intoduction
This repositry consists of utilities built to run static code analysis and unit tests as a part of seperate build using AWS Code build for PR create/update events
and a detailed email report will be sent to authors & reviewers with static code analysis report , unit test report & test coverage report .

## CI/CD
Code build project is setup to to build for any changes and deploy to the appropriate environment , for push events across respective branches. 

## Code Workflow
This uses [Git Ship](https://markshust.com/2018/04/07/introducing-git-ship-simplified-git-flow-workflow/) for git workflow. 
Master branch is both the main and development branch. 
All feature and bugfix branches needs to be forked from master and merged back into master. 
Any changes to master are deployed automatically to developement environment.
Release branches will be created from master to different environment (Production and Staging).

## Code
The code is written in Python.

##### Feature Flags and default setup

```
AUTO_MERGE = True
AUTO_APPROVE = True
EMAIL_REPORT = True
PR_COMMENT = True
AUTO_DECLINE = False 
```

## pylint.rcfile
A custom cofig file consisting of BHB's python coding standards!
Analysis will be done basing this as a reference file .


## AWS Services
The application uses AWS CodeBuild ,SES (Simple Email Service)

## Initial Setup
Conditoinal cloning in docker files~

```
ARG staticcodeanalysis
COPY code-build-utils/setup-code-analysis.sh setup-code-analysis.sh
RUN if [ "$staticcodeanalysis" = "1" ] ; then ./setup-code-analysis.sh ;   else echo Not cloning static code analysis repo  ; fi
```
Only when "staticcodeanalysis" is set as 1 in build command, the repo will be cloned!
```
docker build -t name . --build-arg staticcodeanalysis=1
```
##### setup-code-analysis.sh
```
#!/bin/bash
git clone https://deployuserbhb:da45!Fh6@bitbucket.org/bensonhillbiosystems/staticcodeanalysis.git;
pip3 install -r staticcodeanalysis/requirements.txt ;

```

## Contributors
 - Lakshmi Naarayanan

## Future Wo

## Repository
 - https://bitbucket.org/bensonhillbiosystems/staticcodeanalysis
