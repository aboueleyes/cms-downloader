#!/usr/bin/env python3
import argparse
import sys
from signal import SIGINT, signal

import urllib3
from rich import print
from rich.console import Console

from cms import (HOST, HttpNtlmAuth, authenticate_user, bs, choose_course,
                 choose_files, download_files, filter_downloads,
                 get_announcments, get_avaliable_courses, get_course_names,
                 get_course_soup, get_credinalities, get_display_items,
                 get_downloded_items, get_files, make_courses_dir, os,
                 requests)


def handler(signal_received, frame):
    # Handle any cleanup here
    print('\n[red][bold]SIGINT or CTRL-C detected. Exiting[/bold][/red]')
    sys.exit(0)


def print_annoencemnt(course, username, password, course_url, session):
    '''print the annoencment'''
    annoencments = get_announcments(get_course_soup(
        course_url, username, password, session))
    console = Console()
    console.print(f'[bold][red]{course}[/red][/bold]\n', justify='center')
    to_print = ''
    for item in annoencments:
        if item == '':
            continue
        to_print += item.strip()
        console.print(item.strip(), justify='center')


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
    praser.add_argument('-n', '--new', help='display annoencment of the course',
                        action='store_true', default=False)
    args = praser.parse_args()

    # Disable warnings because SSL
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    username, password = get_credinalities()

    if authenticate_user(username, password):
        print("[+] Authorized")
    else:
        print("[!] you are not authorized. review your credentials")
        os.remove(".env")
        sys.exit(1)

    session = requests.Session()
    home_page = session.get(HOST,
                            verify=False, auth=HttpNtlmAuth(username, password))
    home_page_soup = bs(home_page.text, 'html.parser')

    course_links = get_avaliable_courses(home_page_soup)
    courses_name = get_course_names(home_page_soup)
    make_courses_dir(courses_name)

    if args.pdf or args.all:
        if args.new:
            for index, course_url in enumerate(course_links):
                print_annoencemnt(
                    courses_name[index], username, password, course_url, session)
                print()
            sys.exit(0)
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
        if args.new:
            print_annoencemnt(course, username, password, course_url, session)
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
