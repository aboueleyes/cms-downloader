# imports
import getpass
import json
import os
import re
import urllib.request

from sanitize_filename import sanitize
import requests
import urllib3
from bs4 import BeautifulSoup as bs
from iterfzf import iterfzf
from requests_ntlm import HttpNtlmAuth
from tqdm import tqdm

# Disabling warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def login():
    if not os.path.isfile(".credenalites"):
        username = input("Enter your username : ")
        password = getpass.getpass(prompt="Enter Your Password : ")
        f = open(".credenalites", "w")
        f.write(username+"\n"+password)
        f.close()
    else:
        f = open(".credenalites", "r")
        lines = f.readlines()
        username = lines[0].strip()
        password = lines[1].strip()
        f.close()
    return username, password


username, password = login()


def req_session():
    session = requests.Session()
    homePage = session.get("https://cms.guc.edu.eg/",
                           verify=False, auth=HttpNtlmAuth(username, password))
    homePage_soup = bs(homePage.text, 'html.parser')
    return homePage_soup, session


homePage_soup, session = req_session()


def getCoursesName():
    coursesTable = list(homePage_soup.find('table', {
        'id': 'ContentPlaceHolderright_ContentPlaceHoldercontent_GridViewcourses'}))
    courses_name = []
    for i in range(2, len(coursesTable) - 1):
        courses_name.append(re.sub(
            r'\n*[\(][\|]([^\|]*)[\|][\)]([^\(]*)[\(].*\n*', '[\\1]\\2', coursesTable[i].text))
    return courses_name


def getAvaliableCourses():
    print("[-] Fetching Courses")
    course_links = []
    link_tags = homePage_soup('a')
    for i, link_tag in enumerate(link_tags):
        ans = link_tag.get('href', None)
        if ans == None:
            continue
        match = re.match(r'\/apps\/student\/CourseViewStn\?id(.*)', ans)
        if match:
            course_links.append("https://cms.guc.edu.eg"+ans)
    return course_links


def chooseCourse():
    if not os.path.isfile(".courses.json"):
        courses_links = getAvaliableCourses()
        courses_names = getCoursesName()
        courses = dict(zip(courses_names, courses_links))
        with open(".courses.json", "w") as outfile:
            json.dump(courses, outfile)
        os.makedirs("Downloads")
        for dir in courses_names:
            if not os.path.exists(dir):
                os.makedirs("Downloads/"+dir)
    with open('.courses.json') as json_file:
        Links = json.load(json_file)
    courses = []
    for i in Links:
        courses.append(i)
    course = iterfzf(courses)
    os.chdir("Downloads/"+course)
    course_url = Links.get(course)
    return course_url


def getFiles():
    download_links, download_names, discreption = [], [], []
    coursePage = session.get(chooseCourse(), verify=False,
                             auth=HttpNtlmAuth(username, password))
    coursePage_soup = bs(coursePage.text, 'html.parser')
    files_body = coursePage_soup.find_all(class_="card-body")
    for i in files_body:
        discreption.append(
            re.sub(r'[0-9]* - (.*)', "\\1", i.find("div").text).strip())
        download_links.append("https://cms.guc.edu.eg"+i.find('a').get("href"))
        download_names.append(
            re.sub(r'[0-9]* - (.*)', "\\1", i.find("strong").text).strip())

    return download_links, download_names, discreption


def chooseFiles():
    download_links, download_names, discreption = getFiles()
    zipped = zip(discreption, download_links, download_names)
    zipped = sorted(zipped)
    discreption, download_links, download_names = zip(*zipped)
    items_to_download_names = iterfzf(discreption, multi=True)
    item_links = []
    item_names = []
    for i in items_to_download_names:
        index = discreption.index(i)
        item_link = download_links[index]
        item_name = download_names[index]
        item_links.append(item_link)
        item_names.append(item_name)
    return item_links, item_names


def downloadFiles():
    files_download_links, file_names = chooseFiles()
    for i in range(len(files_download_links)):
        url = files_download_links[i]
        file_ext = url[-4:]
        file_name = sanitize(file_names[i]+file_ext)
        if os.path.isfile(file_name):
            print("file already exists skipped")
            continue
        r = requests.get(url, auth=HttpNtlmAuth(
            username, password), verify=False, stream=True, allow_redirects=True)
        total_size = int(r.headers.get('content-length'))
        initial_pos = 0
        if r.status_code == 200:
            with open(file_name, 'wb') as f:
                with tqdm(total=total_size, unit="B",
                          unit_scale=True, desc=file_name, initial=initial_pos, ascii=True) as pbar:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
        else:
            print("error please try again")


if __name__ == "__main__":
    downloadFiles()
