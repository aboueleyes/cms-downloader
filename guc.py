"""[Classes of The DownloadFile and DownloadList]"""
import os

from sanitize_filename import sanitize

DOWNLOADS_DIR = 'Downloads'


class DownloadFile:
    """[A File dataType]
    """

    def __init__(self, name, url, discreption, week):
        """[Constructor]

        Args:
            name ([String]): [name of a File]
            url ([String]): [The url of a File]
            discreption ([String]): [The Discreption of the File]
            week ([String]): [The week number of The File]
        """
        self.name = name
        self.url = url
        self.ext = ''
        self.discreption = discreption
        self.week = week
        self.course = ''
        self.path = ''

    def normalize(self):
        """[Update The extension and the week and path of the file]
        """
        self.ext = '.' + self.url.rsplit('.', 1)[1]
        self.week = sanitize(self.week)
        self.path = f'{DOWNLOADS_DIR}/{self.course}/{self.week}/\
        {sanitize(self.name)+sanitize(self.ext)}'


class DownloadList:
    """[A list of of DownloadsFile]
    """

    def __init__(self):
        """[Simple Constructor]
        """
        self.list = []

    def get_names(self):
        """[return the names of the files]

        Returns:
            [List]: [List of names of the files]
        """
        return [item.name for item in self.list]

    def get_descriptions(self):
        """[return the descriptions of the files]

        Returns:
            [List]: [List of names of the files]
        """
        return [item.discreption for item in self.list]

    def get_week(self):
        """[return the weeks of files]

        Returns:
            [List]: [List of weeks of the files]
        """
        return [item.week for item in self.list]

    def make_weeks(self):
        """[make the weeks for the files]
        """
        for item in self.list:
            try:
                os.makedirs(
                    f"{DOWNLOADS_DIR}/{item.course}/{sanitize(item.week)}")
            except FileExistsError:
                pass
