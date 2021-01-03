import boto3
import base64
from botocore.exceptions import ClientError


def get_secret():

    secret_name = "StaticCodeAnalysisSecrets"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        return get_secret_value_response['SecretString']
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            
    # Your code goes here. 
SECRETS = get_secret()


#BITBUCKET CONFIGS
CLIENT_KEY = SECRETS['BITBUCKET_CLIENT_KEY']
CLIENT_SECRET_ID =SECRETS['BITBUCKET_CLIENT_SECRET_ID']

#AWS CONFIG
ACCESS_KEY = SECRETS['AWS_ACCESS_KEY']
SECRET_KEY=SECRETS['AWS_SECRET_KEY']
AWS_REGION = "us-east-1"

#Bitbucket Team
OWNER_NAME = 'iamlmn'
#Unit test dir
TEST_DIR = "/home/pipeline/test/"

# AWS ,EMAIL & MODULE SETTINGS
SENDER = "lakshminaarayananvs@rediffmail.com"
#MODULES=['rungwas.py', 'gemma_run.py', 'csv_conversion.py', 'plink_conversion.py', 'Poorly_coded.py']
MODULES=['run.py', 'main.py', 'train.py', 'test.py']
TO=['lakshminaarayananvs@rediffmail.com']
PYLINT_REPORT_NAME='Module_pylint_Code_Analysis'
    
#Base Email subject
SUBJECT = "Static Code Analysis"

#Pylint config
PYLINT_MIN_SCORE = 9
PYLINT_CONFIG_FILE = "staticcodeanalysis/config.pylintrc"

ATTACHMENT = [PYLINT_REPORT_NAME+'.html']
BODY_TEXT = "Hello,\r\nPlease see the attached file for a list of customers to contact."
CHARSET = "utf-8"

#Code Analysis Feature config
AUTO_MERGE = True
AUTO_APPROVE = True
EMAIL_REPORT = True
PR_COMMENT = True
AUTO_DECLINE = False
