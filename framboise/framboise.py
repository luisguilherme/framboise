from exceptions import StandardError
from functools import partial
from itertools import imap, ifilter
import logging
from logging import info, warning, error, basicConfig
from operator import attrgetter, itemgetter, le
import os
import pprint
from subprocess import Popen, PIPE
import sys
import xmlrpclib

from opensubtitles import hasher

USER_AGENT = 'OS Test User Agent'
XMLRPC_URI = 'http://api.opensubtitles.org/xml-rpc'
CR_USER = ''
CR_PASS = ''
LANG = 'pb'
VTYPES = ['3g2', '3gp', '3gp2', '3gpp', '60d', 'ajp', 'asf', 'asx', 'avchd', 
          'avi', 'bik', 'bix', 'box', 'cam', 'dat', 'divx', 'dmf', 'dv', 
          'dvr-ms', 'evo', 'flc', 'fli', 'flic', 'flv', 'flx', 'gvi', 'gvp', 
          'h264', 'm1v', 'm2p', 'm2ts', 'm2v', 'm4e', 'm4v', 'mjp', 'mjpeg', 
          'mjpg', 'mkv', 'moov', 'mov', 'movhd', 'movie', 'movx', 'mp4', 
          'mpe', 'mpeg', 'mpg', 'mpv', 'mpv2', 'mxf', 'nsv', 'nut', 'ogg', 
          'ogm', 'omf', 'ps', 'qt', 'ram', 'rm', 'rmvb', 'swf', 'ts', 'vfw', 
          'vid', 'video', 'viv', 'vivo', 'vob', 'vro', 'wm', 'wmv', 'wmx', 
          'wrap', 'wvx', 'wx', 'x264', 'xvid']
STYPES = ['aqt', 'jss', 'sub', 'ttxt', 'pjs', 'psb', 'rt', 'smi', 'ssf', 
          'srt', 'gsub', 'ssa', 'ass', 'usf', 'stl']

# Sorts list of results by:
#  - Language
#  - Rating
class Sorter():
    def __init__(self, langs='all'):
        print "Available languages: ", langs
        self.langs = langs.split(',')
 
    def bestfn(self, subentry, prefix=''):
        idx = self.langs.index(subentry['SubLanguageID'])
        value = (idx if idx >= 0 else len(self.langs))
        return value

class CredentialsError(StandardError):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)


def require_login(f):
    def wrapper(self, *args, **kwargs):
        if not self.logged_in:
            self.__log_in__()
        return f(self, *args, **kwargs)
    return wrapper

class Downloader():
    def __init__(self, langs='all', sorter=None, cr_user='', cr_pass='',
                 os_language='en'):
        self.langs = langs
        self.cr_user = cr_user
        self.cr_pass = cr_pass
        self.os_language = os_language
        
        self.sorter = sorter if sorter is not None else Sorter(langs)
        
        self.logged_in = False
        basicConfig(level=logging.INFO)
        
    def __log_in__(self):
        self.server = xmlrpclib.ServerProxy(XMLRPC_URI)
        login = self.server.LogIn(self.cr_user, self.cr_pass, 
                                  self.os_language, USER_AGENT)

        if int(login['status'].split(' ')[0]) / 100 != 2:
            error("Couldn't log in")
            raise CredentialsError("Couldn't log in")
        
        self.token = login['token']
        info("Logged in with token {}".format(self.token))
        self.logged_in = True        

    @require_login
    def get_subs(self, movie_file):
        file_name = os.path.basename(movie_file)
        #file_root, movie_ext = os.path.splitext(file_name)
        hash = hasher.hashFile(movie_file)
        size = str(os.path.getsize(movie_file))
#        if size > sys.maxint:
#            warning("File {} is huge ({}b)".format(file_name, size))
#            return []
        search_query = {'sublanguageid': self.langs,
                        'moviehash': hash,
                        'moviebytesize': size}

        result = self.server.SearchSubtitles(self.token, [search_query])
        if result['data'] == 'False' or not result['data']:
            info("No data found for file {}".format(file_name))
            return []
         
        info("Found {} results".format(len(result['data'])))
        return result['data']

    def get_best_sub(self, movie_file):
        file_root, movie_ext = os.path.splitext(movie_file)

        if any(map(os.path.exists, 
                   (file_root + '.' + subext for subext in STYPES))):
             warning("Subtitle exists for movie {}".format(
                 os.path.basename(movie_file)))
             return None

        results = self.get_subs(movie_file)
        if not results:
            return None
        best = min(results, key=self.sorter.bestfn)
        
        print "Found subtitle in {lang} for movie {mn}:\n {link} => {d}"\
             .format(lang=best['LanguageName'], mn=best['MovieName'],
                     link=best['SubDownloadLink'], 
                     d=file_root + '.' + best['SubFormat'])

        file_name = file_root + '.' + best['SubFormat'] 
        
        with open(file_name, 'w') as subfile:
            wget = Popen(["wget", "-O", "-", best['SubDownloadLink']], 
                         stdout=PIPE, stderr=open(os.devnull, 'w'))
            gunz = Popen(["gunzip", "-c"], stdin=wget.stdout, stdout=subfile)
            print "Subtitle saved as {filename}".format(filename=file_name)
        return file_name


def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    spath = argv[1]
    langs = argv[2]
    
    files = [os.path.join(p, f) for p,fl in 
             imap(itemgetter(0,2), os.walk(spath))
             for f in fl if f.split('.')[-1] in VTYPES]
    
    downloader = Downloader(langs)
    for movie_file in files:
        downloader.get_best_sub(movie_file)

if __name__ == '__main__':
    main(sys.argv)

