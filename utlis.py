import re
import os
import requests
from PyInquirer import prompt
from requests_ntlm import HttpNtlmAuth

def authenticate_user(username, password):
    '''validate user credentials'''
    session = requests.Session()
    request_session = session.get("https://cms.guc.edu.eg/",
                    verify=False, auth=HttpNtlmAuth(username, password))
    if request_session.status_code == 200:
        return True
    return False


def get_credinalities():
    '''login to cms website'''
    try:
        file_env = open(".env", "r")
        lines = file_env.readlines()
        user_name = lines[0].strip()
        pass_word = lines[1].strip()
        authenticate_user(user_name, pass_word)
        file_env.close()
    except:
        questions = [
            {
                'type': 'input',
                'name': 'username',
                'message': 'Enter your GUC username:',
            },
            {
                'type': 'password',
                'message': 'Enter your GUC password:',
                'name': 'password'
            }
        ]
        cred = prompt(questions)
        user_name = list(cred.values())[0]
        pass_word = list(cred.values())[1]
        authenticate_user(user_name, pass_word)
        file_env = open(".env", "w")
        file_env.write(user_name+"\n"+str(pass_word))
        file_env.close()
    return user_name, pass_word


def get_avaliable_courses(home_page_soup):
    '''fetch courses links'''
    course_links = []
    link_tags = home_page_soup('a')
    for link_tag in link_tags:
        ans = link_tag.get('href', None)
        if ans is None:
            continue
        match = re.match(r'\/apps\/student\/CourseViewStn\?id(.*)', ans)
        if match:
            course_links.append(ans)
    return course_links
