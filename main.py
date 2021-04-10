#!/usr/bin/env python3
import argparse
import sys
import time
from signal import SIGINT, signal

import urllib3

from cms import *


def handler(signal_received, frame):
    # Handle any cleanup here
    print('\nSIGINT or CTRL-C detected. Exiting gracefully')
    sys.exit(0)


def main():

    praser = argparse.ArgumentParser(prog='cms-downloader', description=''' 
        Download Material from CMS website
    ''')
    praser.add_argument('-p', '--pdf', help='download all pdf files',
                        action='store_true', default=False)
    praser.add_argument('-a', '--all', help='download all files',
                        action='store_true', default=False)
    praser.add_argument('-f', '--filter', help='display only new files',
                        action='store_true', default=False)

    args = praser.parse_args()

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    username, password = get_credinalities()
    if authenticate_user(username, password):
        print("[+] Authorized")
    else:
        print("[!] you are not authorized. review your credentials")
        os.remove(".env")
        sys.exit(1)

    session = requests.Session()
    home_page = session.get("https://cms.guc.edu.eg/",
                            verify=False, auth=HttpNtlmAuth(username, password))
    home_page_soup = bs(home_page.text, 'html.parser')

    course_links = get_avaliable_courses(home_page_soup)
    courses_name = get_course_names(home_page_soup)
    make_courses_dir(courses_name)
    if args.pdf or args.all:
        for index, course in enumerate(course_links):
            files = get_files(course, username, password, session)
            for item in files.list:
                item.course = courses_name[index]
            files.make_weeks()
            if args.all:
                download_files(files.list, username, password)
            else:
                download_files(files.list, username, password, pdf=True)
    else:
        course_url, course = choose_course(courses_name, course_links)
         # print(item forcitem in get_announcments(get_course_soup(course_url, username, password, session)))
        for item in get_announcments(get_course_soup(course_url, username, password, session)):
            print(item,end=" ")
        print()
        sys.exit(0)
        files = get_files(course_url, username, password, session)
        for item in files.list:
            item.course = course
        files.make_weeks()
        if args.filter:
            already_downloaded = get_downloded_items(course)
            filtered = filter_downloads(files, already_downloaded)
            files_to_display = get_display_items(files, filtered)
            files_to_download = choose_files(files_to_display)
        else:
            files_to_download = choose_files(files)
        download_files(files_to_download.list, username, password)


if __name__ == "__main__":
    signal(SIGINT, handler)
    main()
