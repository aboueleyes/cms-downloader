import os

from sanitize_filename import sanitize


class DownloadFile:

    def __init__(self):
        self.name = ''
        self.url = ''
        self.ext = ''
        self.discreption = ''
        self.week = ''
        self.course = ''
        self.path = ''

    def set_ext(self):
        self.ext = '.' + self.url.rsplit('.', 1)[1]

    def set_week(self):
        self.week = sanitize(self.week)

    def set_path(self):
        self.path = f'Downloads/{self.course}/{self.week}/{sanitize({self.name + self.ext})}'


class DownloadList:
    def __init__(self):
        self.list = []

    def get_names(self):
        return [item.name for item in self.list]

    def get_discrepitions(self):
        return [item.discreption for item in self.list]

    def get_week(self):
        return [item.week for item in self.list]

    def make_weeks(self):

        for item in self.list:
            if not os.path.exists(f"Downloads/{item.course}/{sanitize(item.week)}"):
                os.makedirs(f"Downloads/{item.course}/{sanitize(item.week)}")
