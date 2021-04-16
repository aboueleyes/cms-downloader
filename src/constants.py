DOWNLOADS_DIR = 'Downloads'

HOST = 'https://cms.guc.edu.eg'
COURSE_REGEX ="\n*[\(][\|]([^\|]*)[\|][\)]([^\(]*)[\(].*\n*"
COURSE_REPALCE='[\\1]\\2'

# for GIU uncomment the following lines 
# HOST='https://cms.giu-uni.de'
# COURSE_REGEX ="\n*(.*)acti"
# COURSE_REPALCE='\\1'
