#!/usr/bin/env python3
import sys
import time
from signal import SIGINT, signal

import urllib3

from cms import *

# from rich import print
# from rich.console import Console



def handler(signal_received, frame):
    # Handle any cleanup here
    print('\nSIGINT or CTRL-C detected. Exiting gracefully')
    sys.exit(0)


def main():

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

    course_url, course = choose_course(courses_name, course_links)

    files = get_files(course_url, username, password, session)
    files_to_download = choose_files(files)

    for item in files_to_download.list:
        item.course = course
    files_to_download.make_weeks()
    download_files(files_to_download.list, username, password)
if __name__ == "__main__":
    signal(SIGINT, handler)
    main()
