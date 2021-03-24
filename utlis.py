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
def get_course_names(home_page_soup):
    '''get courses names'''
    courses_table = list(home_page_soup.find('table', {
        'id': 'ContentPlaceHolderright_ContentPlaceHoldercontent_GridViewcourses'}))
    courses_name = []
    for i in range(2, len(courses_table) - 1):
        courses_name.append(re.sub(
            r'\n*[\(][\|]([^\|]*)[\|][\)]([^\(]*)[\(].*\n*', '[\\1]\\2', courses_table[i].text))
    return courses_name

def choose_course(courses_name,courses_links):
    '''promt the user to choose the string'''
    if not os.path.isfile(".courses.json"):
        courses = dict(zip(courses_names, courses_links))
        with open(".courses.json", "w") as outfile:
            json.dump(courses, outfile)
    with open('.courses.json') as json_file:
        links = json.load(json_file)
    courses = []
    for i in links:
        courses.append(i)
    questions = [
        {
            'type': 'list',
            'name': 'size',
            'message': 'What Course do you want?',
            'choices': courses
        }
    ]
    course = prompt(questions)
    course = list(course.values())[0]
    course_url = links.get(course)
    return course_url
