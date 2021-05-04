#!/usr/bin/env python3
"""A Python Script to download material from cms-website"""
import argparse
import sys
from signal import SIGINT, signal

import urllib3
from rich import print as r_print
from rich.console import Console

from src.cms import (HOST, HttpNtlmAuth, authenticate_user, bs, choose_course,
                     choose_files, download_files, filter_downloads,
                     get_avaliable_courses, get_cardinalities,
                     get_course_names, get_display_items, get_downloaded_items,
                     get_files, make_courses_dir, os, print_announcement,
                     requests, BACK)


def handler(_, __):
    """Handle SIGINT signals"""
    r_print('\n[red][bold]SIGINT or CTRL-C detected. Exiting[/bold][/red]')
    sys.exit(0)



def download_all():
    for index, course in enumerate(course_links):
        files = get_files(course, username, password, session)
        for item in files.list:
            item.course = courses_name[index]
        files.make_weeks()
        if args.all:
            download_files(files.list, username, password)
        else:
            download_files(files.list, username, password, pdf=True)


def diplay_announcements():
    for index, course_url in enumerate(course_links):
        print_announcement(
            courses_name[index], username, password, course_url, session, console)


def interactive():
    while True:
        course_url, course = choose_course(courses_name, course_links)
        files = get_files(course_url, username, password, session)
        for item in files.list:
            item.course = course
        files.make_weeks()
        files_to_download = choose_files(files)
        if files_to_download != BACK:
            download_files(files_to_download.list, username, password)
            sys.exit(0)


def filter_interactive():
    while True:
        course_url, course = choose_course(courses_name, course_links)
        files = get_files(course_url, username, password, session)
        for item in files.list:
            item.course = course
            files.make_weeks()
        already_downloaded = get_downloaded_items(course)
        filtered = filter_downloads(files, already_downloaded)
        files_to_display = get_display_items(files, filtered)
        files_to_download = choose_files(files_to_display)
        if files_to_download != BACK:
            download_files(files_to_download.list, username, password)
            sys.exit(0)


if __name__ == "__main__":
    signal(SIGINT, handler)
    console = Console()

    parser = argparse.ArgumentParser(prog='cms-downloader', description='''
        Download Material from CMS website
    ''')
    parser.add_argument('-p', '--pdf', help='download all pdf files',
                        action='store_true', default=False)
    parser.add_argument('-a', '--all', help='download all files',
                        action='store_true', default=False)
    parser.add_argument('-f', '--filter', help='display only new files',
                        action='store_true', default=False)
    parser.add_argument('-n', '--new', help='display announcement of the course',
                        action='store_true', default=False)
    args = parser.parse_args()

    # Disable warnings because SSL
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    username, password = get_cardinalities()

    if authenticate_user(username, password):
        console.rule("[+] Authorized", style='bold green')
    else:
        console.rule(
            "[!] you are not authorized. review your credentials", style='bold red')
        os.remove(".env")
        sys.exit(1)

    session = requests.Session()
    home_page = session.get(HOST,
                            verify=False, auth=HttpNtlmAuth(username, password))
    home_page_soup = bs(home_page.text, 'html.parser')

    course_links = get_avaliable_courses(home_page_soup)
    courses_name = get_course_names(home_page_soup)
    make_courses_dir(courses_name)
    if args.all or args.pdf:
        download_all()
    elif args.new:
        diplay_announcements()
    elif args.filter:
        filter_interactive()
    else :
        interactive()
