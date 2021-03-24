import json
import os
import re

import requests
from bs4 import BeautifulSoup as bs
from iterfzf import iterfzf
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


def choose_course(courses_names, courses_links):
    ''' prompt the user a list to choose the link '''
    if not os.path.isfile(".courses.json"):
        courses = dict(zip(courses_names, courses_links))
        with open(".courses.json", "w") as outfile:
            json.dump(courses, outfile)
        os.makedirs("Downloads")
        for directly in courses_names:
            if not os.path.exists(directly):
                os.makedirs("Downloads/"+directly)
    with open('.courses.json') as json_file:
        course_items = json.load(json_file)
    courses = []
    for i in course_items:
        courses.append(i)
    course = iterfzf(courses)
    os.chdir("Downloads/"+course)
    course_url = course_items.get(course)
    return course_url


def get_files(course_url, course_page_soup, username, password, session):
    '''get filename and links and description'''
    download_links, download_names, discreption = [], [], []
    course_page = session.get(course_url, verify=False,
                              auth=HttpNtlmAuth(username, password))
    course_page_soup = bs(course_page.text, 'html.parser')
    files_body = course_page_soup.find_all(class_="card-body")
    for i in files_body:
        discreption.append(
            re.sub(r'[0-9]* - (.*)', "\\1", i.find("div").text).strip())
        download_links.append("https://cms.guc.edu.eg"+i.find('a').get("href"))
        download_names.append(
            re.sub(r'[0-9]* - (.*)', "\\1", i.find("strong").text).strip())

    return download_links, download_names, discreption
