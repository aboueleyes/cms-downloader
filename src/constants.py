DOWNLOADS_DIR = 'Downloads'

HOST = 'https://cms.guc.edu.eg'
COURSE_REGEX = r"\n*[\(][\|]([^\|]*)[\|][\)]([^\(]*)[\(].*\n*"
COURSE_REPALCE = '[\\1]\\2'

# # for GIU uncomment the following lines
# HOST='https://cms.giu-uni.de'
# COURSE_REGEX ="\n*(.*)Acti.*"
# COURSE_REPALCE='\\1'
