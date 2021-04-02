#!/usr/bin/env python3
import sys
import time
from signal import SIGINT, signal

import urllib3
from rich import print
from rich.console import Console

from utlis import *


def handler(signal_received, frame):
    # Handle any cleanup here
    print('\n[bold]SIGINT or CTRL-C detected. [red]Exiting gracefully[/red][/bold]')
    sys.exit(0)


def main():
    # Disable Warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # get username, password and authenticate user
    username, password = get_credinalities()

    if authenticate_user(username, password):
        console.rule("[+] Authorized", style="bold green")
    else:
        console.rule(
            "[!] you are not authorized. review your credentials", style="bold red")
        os.remove(".env")
        sys.exit(1)
    session = requests.Session()
    home_page = session.get("https://cms.guc.edu.eg/",
                            verify=False, auth=HttpNtlmAuth(username, password))
    home_page_soup = bs(home_page.text, 'html.parser')

    course_links = get_avaliable_courses(home_page_soup)
    courses_name = get_course_names(home_page_soup)

    course_url,course= choose_course(courses_name, course_links)
    download_links, download_names, discreption, week_name = get_files(
        course_url, username, password, session)

    item_links, item_names, week_name = choose_files(
        download_links, download_names, discreption, week_name)
    week_name = sanitize_files(week_name)
    week_dir(week_name, course)
    download_files(item_links, item_names, week_name, username, password,course)


if __name__ == '__main__':
    console = Console()
    signal(SIGINT, handler)
    main()
