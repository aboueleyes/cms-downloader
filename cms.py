
import getpass
import json
import os
import re
import threading

import requests
from bs4 import BeautifulSoup as bs
from iterfzf import iterfzf
from requests_ntlm import HttpNtlmAuth
from sanitize_filename import sanitize
from tqdm import tqdm

from Guc import DownloadFile, DownloadList


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
        cred = (lines[0].strip(), lines[1].strip())
        file_env.close()
    except:
        cred = (input("Enter Your GUC username :  "),
                getpass.getpass(prompt="Enter Your GUC Password : "))
        file_env = open(".env", "w")
        file_env.write(f"{cred[0]}\n{cred[1]}")
        file_env.close()
        # TODO remove PyInquirer and retrun tuple, improve code
    return cred


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
            course_links.append("https://cms.guc.edu.eg"+ans)
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
        if not os.path.exists("Downloads"):
            os.makedirs("Downloads")
        for directly in courses_names:
            if not os.path.exists("Downloads/"+directly):
                os.makedirs("Downloads/"+directly)
    with open('.courses.json') as json_file:
        course_items = json.load(json_file)
    courses = []
    for i in course_items:
        courses.append(i)
    course = iterfzf(courses)
    course_url = course_items.get(course)
    return course_url, course


def get_files(course_url, username, password, session):
    '''get filename link and description'''
    files = DownloadList()

    course_page = session.get(course_url, verify=False,
                              auth=HttpNtlmAuth(username, password))
    course_page_soup = bs(course_page.text, 'html.parser')
    files_body = course_page_soup.find_all(class_="card-body")
    for j, i in enumerate(files_body):
        files.list.append(DownloadFile())
        files.list[j].url = ("https://cms.guc.edu.eg"+i.find('a').get("href"))
        files.list[j].week = i.parent.parent.parent.parent.find('h2').text
        files.list[j].discreption = re.sub(
            r'[0-9]* - (.*)', "\\1", i.find("div").text)
        files.list[j].name = re.sub(
            r'[0-9]* - (.*)', "\\1", i.find("strong").text)
    return files


def choose_files(downloadfiles):
    items_to_download_names = iterfzf(
        downloadfiles.get_discrepitions(), multi=True)
    files_to_download = DownloadList()
    for i in range(len(downloadfiles.list)):
        for j in range(len(items_to_download_names)):
            if downloadfiles.list[i].discreption == items_to_download_names[j]:
                files_to_download.list.append(downloadfiles.list[i])
    return files_to_download


def check_exists(file_to_download):
    return os.path.isfile(file_to_download)


def download_file(file_to_download, username, password):
    r = requests.get(file_to_download.url, auth=HttpNtlmAuth(
        username, password), verify=False, stream=True, allow_redirects=True)
    total_size = int(r.headers.get('content-length'))
    initial_pos = 0
    with open(file_to_download.path, 'wb') as f:
        with tqdm(total=total_size, unit="B",
                  unit_scale=True, desc=file_to_download.name, initial=initial_pos, ascii=True) as pbar:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))


def download_files(files_to_download, username, password):
    therads = []
    for i in range(len(files_to_download)):
        files_to_download[i].noramlize()
        if check_exists(files_to_download[i].path):
            print("Already exisis")
            continue
        processThread = threading.Thread(
            target=download_file, args=(files_to_download[i], username, password))  # parameters and functions have to be passed separately
        processThread.start()  # start the thread
        therads.append(processThread)
