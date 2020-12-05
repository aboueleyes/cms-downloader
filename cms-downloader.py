#imports
from tqdm import tqdm
import os
import re
from iterfzf import iterfzf
import requests
from requests_ntlm import HttpNtlmAuth
from bs4 import BeautifulSoup as bs
import urllib3
import urllib.request
import json
import getpass
# Disabling warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Credenalites
if not os.path.isfile(".credenalites") :
    username = input("Enter your username : ")
    password = getpass.getpass(prompt="Enter Your Password : ")
    f  = open(".credenalites","w")
    f.write(username+"\n"+password)
    f.close()
else :
    f  = open(".credenalites","r")
    lines=f.readlines()
    username=lines[0].strip()
    password=lines[1].strip()
    f.close()

# Starting the session (logging in the CMS website)
session = requests.Session()
homePage = session.get("https://cms.guc.edu.eg/",
                       verify=False, auth=HttpNtlmAuth(username, password))
homePage_soup = bs(homePage.text, 'html.parser')

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
    for i,link_tag in enumerate(link_tags):
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
        for dir in courses_names :
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
    download_links = []
    download_names = []
    coursePage = session.get(chooseCourse(), verify=False,
                             auth=HttpNtlmAuth(username, password))
    coursePage_soup = bs(coursePage.text, 'html.parser')
    files_body = coursePage_soup.find_all(class_="card-body")
    for i in files_body:
        download_links.append("https://cms.guc.edu.eg"+i.find('a').get("href"))
        download_names.append(
            re.sub(r'[0-9]* - (.*)', "\\1", i.find("strong").text))
    return download_links, download_names


def chooseFiles():
    download_links, download_names = getFiles()
    items_to_download_names = iterfzf(download_names, multi=True)
    item_links = []
    for i in items_to_download_names :
        index = download_names.index(i)
        item_link = download_links[index]
        item_links.append(item_link)
    return item_links, items_to_download_names


def downloadFiles():
    files_download_links, file_names = chooseFiles()
    for i in range(len(files_download_links)):
        url = files_download_links[i]
        file_ext = url[-4:]
        file_name = file_names[i]+file_ext
        if os.path.isfile(file_name) :
            print ("file already exists skipped")
            continue
        if url[-1] == 'v' or url[-1] == '4' :
            print("waiting , Be patient..")
        r = requests.get(url, auth=HttpNtlmAuth(username, password),verify=False)
        total_size_in_bytes= int(r.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        if r.status_code == 200:
            with open(file_name, 'wb') as out:
                print("Downloading "+file_name)
                for bits in r.iter_content() :
                    progress_bar.update(len(bits))
                    out.write(bits)
                progress_bar.close()

downloadFiles()                