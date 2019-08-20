import requests
import json
from BitbucketUsers import users


def get_bitbucket_token(Client_id,Client_secret_key):
    headers={"Content-Type":"application/x-www-form-urlencoded"}
    response=requests.post("https://{}:{}@bitbucket.org/site/oauth2/access_token".format(Client_id,Client_secret_key),data={"grant_type": "client_credentials" },headers=headers)
    print(response)
    if response.status_code != 200 :
        print("Could not get bitbucket token")
        return None
    else:
        print('Successfully recived bitbucket OAuth token')

    return response.json()['access_token']


def approve_pr(owner_name,repo_slug,pr_id,token):
    #To approve PR's using bitbcuket API
    
    headers = {"Authorization": "Bearer {}".format(token)}
    response=requests.post("https://bitbucket.org/!api/2.0/repositories/{}/{}/pullrequests/{}/approve".format(owner_name,repo_slug,pr_id),headers=headers)
    approve_response = response.json()
    if response.status_code == 200 :
        print("{} approved your PR".format(approve_response['user']['display_name']))
        return approve_response['user']['display_name']
    else:
        return None


def approver_emails(owner_name,repo_slug,pr_id,token):
    headers = {"Authorization": "Bearer {}".format(token)}
    pr_response = requests.get("https://bitbucket.org/!api/2.0/repositories/{}/{}/pullrequests/{}".format(owner_name,repo_slug,pr_id),headers=headers).json()
    to_list=[]

    if len(pr_response['participants']) == 0:
        print("No approvers")
        # return default TO list
    else:
        for i in range(0,len(pr_response['participants'])):
            to_list.append(users[pr_response['participants'][i]['user']['display_name']])
            print(to_list)
            #map each name to users in bitbucket users
    return list(set(to_list))


def comment_pr(owner_name,repo_slug,pr_id,token,comment):

    headers = {"Authorization": "Bearer {}".format(token)}
    data={'content':{'raw':str(comment)}}
    comment_response=requests.post("https://bitbucket.org/!api/2.0/repositories/{}/{}/pullrequests/{}/comments".format(owner_name,repo_slug,pr_id),headers=headers , json = data)
    if comment_response.status_code == 201 :
        return True
    else:
        print("Could not comment on {} ".format(PR_ID))
        return False

    

def merge_pr(owner_name,repo_slug,pr_id,token):
    headers = {"Authorization": "Bearer {}".format(token)}
    response=requests.post("https://bitbucket.org/!api/2.0/repositories/{}/{}/pullrequests/{}/merge".format(owner_name,repo_slug,pr_id),headers=headers)
    merge_response = response.json()
    if response.status_code == 200 :
        print("{} merged your PR".format(merge_response['user']['display_name']))
        return merge_response['closed_by']['display_name']
    elif response.status_code == 400 :
        print("Check for conflicts!")
        return "Code Conflicts"
    else:
        print("Failed to merge the PR!")
    return None


def decline_pr():
    headers = {"Authorization": "Bearer {}".format(token)}
    response=requests.post("https://bitbucket.org/!api/2.0/repositories/{}/{}/pullrequests/{}/decline".format(owner_name,repo_slug,pr_id),headers=headers)
    decline_response = response.json()
    if response.status_code == 200 :
        print("{} merged your PR".format(decline_response['user']['display_name']))
        return True
    else:
        print("Failed to merge the PR!")
    return None

def default_reviewers():
    pass
    #/2.0/repositories/{username}/{repo_slug}/default-reviewers/{target_username}


