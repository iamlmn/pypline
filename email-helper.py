import os
import sys
from pylint.lint import Run
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from glob import glob
import BitbucketUtils
import CodeanalysisConfig

#Unit Test configuration
UNIT_TEST_ENABLE = CodeanalysisConfig.UNIT_TEST_ENABLE
if UNIT_TEST_ENABLE == True :
    TEST_DIR = CodeanalysisConfig.TEST_DIR
    sys.path.insert(0, TEST_DIR)
    import unit_test_suite
else:
    print("Unit test check disabled!")

def get_py_files():
    list_of_py_files=[]
    for root, dirs, files in os.walk(os.getcwd()):
        for name in files:
            if name.endswith(".py"):
                list_of_py_files.append(os.path.join(root,name))
    return list_of_py_files

def get_attachments():
    attachments=glob('Gwas_Unit_Test_Report*.html')
    return attachments[0]

# The character encoding for the email.
if __name__ == '__main__':
    #Code build ENVs
    PARAMS = sys.argv[1:]
    print(PARAMS)
    REPO_SLUG = os.path.basename(PARAMS[0])
    PR_ID = PARAMS[1].split('/')[1]
    OWNER_NAME = CodeanalysisConfig.OWNER_NAME
    SOURCE_BRANCH = PARAMS[2].replace('refs/heads/','')
    TARGET_BRANCH = PARAMS[3].replace('refs/heads/','')

    #BITBUCKET CONFIGS
    CLIENT_KEY = CodeanalysisConfig.CLIENT_KEY
    CLIENT_SECRET_ID = CodeanalysisConfig.CLIENT_SECRET_ID
    BITBUCKET_TOKEN = BitbucketUtils.get_bitbucket_token(CLIENT_KEY,CLIENT_SECRET_ID)

    #AWS CONFIG
    ACCESS_KEY = CodeanalysisConfig.ACCESS_KEY
    SECRET_KEY = CodeanalysisConfig.SECRET_KEY

    # AWS ,EMAIL & MODULE SETTINGS
    SENDER = CodeanalysisConfig.SENDER
    MODULES=CodeanalysisConfig.MODULES
    
    TO=CodeanalysisConfig.TO
    TO = list(set(TO + BitbucketUtils.approver_emails(OWNER_NAME,REPO_SLUG,PR_ID,BITBUCKET_TOKEN)))

    PYLINT_REPORT_NAME=CodeanalysisConfig.PYLINT_REPORT_NAME
    RECIPIENT = ', '.join(TO)
    AWS_REGION = CodeanalysisConfig.AWS_REGION
    SUBJECT = CodeanalysisConfig.SUBJECT + str(REPO_SLUG)

    ATTACHMENT = [PYLINT_REPORT_NAME+'.html']
    BODY_TEXT = "Hello,\r\nPlease see the attached file for a list of customers to contact."
    CHARSET = "utf-8"
    POOR_PYLINT_MODULES=[]

    #Pylint score limit
    PYLINT_MIN_SCORE = CodeanalysisConfig.PYLINT_MIN_SCORE

    # Pylint analysis
    MODULE_SCORES = {}
    MODULE_HTML = ''
    PR_COMMENT = 'Pylint scores : \n'
    FLAG=0
    for i in MODULES :
        results= Run([i,'reports=y', 'rc=code-build-utils/config.pylintrc'],do_exit=False)
        MODULE_SCORES[i]=results.linter.stats['global_note']
        #MODULE_HTML=MODULE_HTML+('<p> {} : {:8.3f} /10 </p>'.format(i,MODULE_SCORES[i]))
        MODULE_HTML = MODULE_HTML+('<tr> <td> {}  </td> <td>   {:8.3f} /10 </td> </tr>'.format(i,MODULE_SCORES[i]))
        PR_COMMENT = PR_COMMENT + '\n' + str(i) + ':' +'{:8.3f} /10'.format(MODULE_SCORES[i]) + '\n'
        if results.linter.stats['global_note'] < PYLINT_MIN_SCORE :
            FLAG=1
            POOR_PYLINT_MODULES.append(i)
    if not FLAG :
        APPROVAL='<h4 style="color:green">Well written! :)</h4>'
        #Aprrove PR from deploy user account!
        
    else:
        APPROVAL='<h4 style="color:orange"> Review for coding standards!'
        SUGGESTION='<h3>Suggestions! </h3><p>Check for message/suggestions in the pylint report and <a href="https://www.python.org/dev/peps/pep-0008/">PEP-8 Coding standards Docs. </a> </h5> You can try <a href="https://pypi.org/project/autopep8/">autopep8</a> , a module to convert code into pep8 standards <br> Use these commands to modify modules in-place(aggressive level-2) <h4 style="backgroud-color:gray"> pip install --upgrade autopep8 <br> autopep8 --inplace --aggressive --aggressive {}</h4> </p>'.format(','.join(POOR_PYLINT_MODULES).replace(',',' '))
        APPROVAL=APPROVAL + SUGGESTION
    try:
        if CodeanalysisConfig.PR_COMMENT == True : 
            comment = BitbucketUtils.comment_pr(OWNER_NAME,REPO_SLUG,PR_ID,BITBUCKET_TOKEN,PR_COMMENT)
            print("Commented {}".format(comment))
        else:
            print("PR Comment feature not enabled!")
    except Exception as e:
        print("Could not comment on PR due to {}".format(e))

    #Getting pylint html report
    os.system('pylint {} --reports=y --rcfile=code-build-utils/config.pylintrc --output-format=json | pylint-json2html -o {}.html'.format(','.join(MODULES).replace(',',' '),PYLINT_REPORT_NAME))
    
    #Getting coverage report!
    os.system('coverage run --source=test test/unit_test_suite.py')
    os.system('coverage html')
    os.system('coverage report -m > test_coverage.txt | zip -r htmlcov.zip htmlcov/')
    ATTACHMENT.append('htmlcov/index.html')
    #ATTACHMENT.append('htmlcov.zip')
    #print(os.environ['UNIT_TEST_STATUS'])

    TEST_HTML=''
    if UNIT_TEST_ENABLE == True :

        UNIT_TEST_STATUS,TOTAL_TESTS=unit_test_suite.unit_tests()
        if UNIT_TEST_STATUS == 0 :
            TEST_HTML=('<p style="color:green;"> {}/{} unit tests have passed! PR has been approved! <i class="fa fa-check"></h4> </p>'.format(TOTAL_TESTS,TOTAL_TESTS))
            print("Approving the PR")

            APPROVERS = BitbucketUtils.approve_pr(OWNER_NAME,REPO_SLUG,PR_ID,BITBUCKET_TOKEN)
            if APPROVERS is not None and CodeanalysisConfig.AUTO_APPROVE == True :
                print ("{} Approved ".format(APPROVERS))

            if not FLAG and CodeanalysisConfig.AUTO_MERGE == True :
                PR_MERGER = BitbucketUtils.merge_pr(OWNER_NAME,REPO_SLUG,PR_ID,BITBUCKET_TOKEN)
                if PR_MERGER == 'Code Conflicts' : 
                    TEST_HTML = TEST_HTML + "<p> Could not merge the PR, Please resolve the conflicts</p>"
                elif PR_MERGER is not None :
                    TEST_HTML = TEST_HTML + "<h4> PR has been merged by {} </h4>".format(PR_MERGER)
                else:
                    TEST_HTML = TEST_HTML + "<p> PR is still open , could not merge! </p>"
            elif FLAG :
                TEST_HTML = TEST_HTML + "<p> PR has not been merged since coding standards were not met </p>"
            elif CodeanalysisConfig.AUTO_MERGE == False :
                TEST_HTML = TEST_HTML + "<p> PR is still open , Enable. AUTO_MERGE if needed. </p>"
        else:
            TEST_HTML=('<p style="color:red;"> {}/{} unit tests have failed! </p>'.format(UNIT_TEST_STATUS,TOTAL_TESTS))
            
            if CodeanalysisConfig.AUTO_DECLINE == True : 
                DECLINER = BitbucketUtils.decline_pr(OWNER_NAME,REPO_SLUG,PR_ID,BITBUCKET_TOKEN)
                if DECLINER == True :
                    APPROVAL='<h4 style="color:red">Few unit tests have failed , Declining the PR </h4>'
                else:
                    APPROVAL='<h4 style="color:red">Few unit tests have failed , Could not decline the PR </h4>'   
            else:
                APPROVAL='<h4 style="color:red">Few unit tests have failed , AUTO_DECLINE is disabled . </h4>'
    else:
        print("Unit test check disabled")
        APPROVAL='<h4 style="color:red">No unit tests to run , hence PR will not be merged automatically </h4>'

    BODY_HTML = """\
        <html>
        <head></head>
        <body>
        <h3>Hello ,</h3>
        <p>A pull request has been created/updated against {} repo from {} to {})<br>
        Please find the static code analysis scores for each python module (pylint) and unit test result for the same!</p>
        <table style="border-collapse:collape" cellspacing="5">
            <tr>
                <th>Module</th>
                <th>Score</th>
            </tr>
            {}
        </table>

        {}
        {}
        <br><h4>Regards,<br>CropOS Platform Engineering</h4>
        </body>
        </html>
""".format(REPO_SLUG , SOURCE_BRANCH , TARGET_BRANCH , MODULE_HTML , TEST_HTML , APPROVAL)

    client = boto3.client('ses',region_name=AWS_REGION,aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY)

    msg = MIMEMultipart('mixed')
    msg['Subject'] = SUBJECT 
    msg['From'] = SENDER 
    msg['To'] = RECIPIENT
    msg_body = MIMEMultipart('alternative')
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)
    ATTACHMENT.append(get_attachments())
    # Define the attachment part and encode it using MIMEApplication.
    #if len(ATTACHMENT) >1 :
    for i in ATTACHMENT:
        att = MIMEApplication(open(i, 'rb').read())
        att.add_header('Content-Disposition','attachment',filename=os.path.basename(i))
        msg.attach(att)
    # else
    # att = MIMEApplication(open(ATTACHMENT, 'rb').read())
    # att.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT))
    # msg.attach(att)

    msg.attach(msg_body)

    #print(msg)
    try:
        #Provide the contents of the email.
        if CodeanalysisConfig.EMAIL_REPORT == True :
            response = client.send_raw_email(
                Source=SENDER,
                Destinations=TO
                ,
                RawMessage={
                    'Data':msg.as_string(),
                }
                #ConfigurationSetName=CONFIGURATION_SET
            )
        else:
            print ("Email Reports not subscribed!")
            sys.exit(0)
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
    # 