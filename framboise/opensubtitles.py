from exceptions import StandardError
import gzip
import logging
import os
from subprocess import Popen, PIPE
import urllib2
import xmlrpclib
import zlib

import chksum
from sorting import DefaultSorter

USER_AGENT = 'OS Test User Agent'
XMLRPC_URI = 'http://api.opensubtitles.org/xml-rpc'
STYPES = ['aqt', 'jss', 'sub', 'ttxt', 'pjs', 'psb', 'rt', 'smi', 'ssf', 
          'srt', 'gsub', 'ssa', 'ass', 'usf', 'stl']

class CredentialsError(StandardError):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)


class Downloader():
    def __init__(self, langs='all', sorter=None, cr_user='', cr_pass='',
                 os_language='en'):
        self.langs = langs
        self.cr_user = cr_user
        self.cr_pass = cr_pass
        self.os_language = os_language
        
        self.sorter = sorter if sorter is not None else DefaultSorter(langs)
        
        self.logged_in = False
        logging.basicConfig(level=logging.INFO)
        
    def __log_in__(self):
        self.server = xmlrpclib.ServerProxy(XMLRPC_URI)
        login = self.server.LogIn(self.cr_user, self.cr_pass, 
                                  self.os_language, USER_AGENT)
        
        if int(login['status'].split(' ')[0]) / 100 != 2:
            error("Couldn't log in")
            raise CredentialsError("Couldn't log in")
        
        self.token = login['token']
        logging.info("Logged in with token {}".format(self.token))
        self.logged_in = True        

    def require_login(f):
        def wrapper(self, *args, **kwargs):
            if not self.logged_in:
                self.__log_in__()
            return f(self, *args, **kwargs)
        return wrapper

    @require_login
    def get_subs(self, movie_file):
        file_name = os.path.basename(movie_file)
        movie_hash = chksum.os_hash(movie_file) 
        size = str(os.path.getsize(movie_file))
        
        search_query = {'sublanguageid': self.langs,
                        'moviehash': movie_hash,
                        'moviebytesize': size}

        result = self.server.SearchSubtitles(self.token, [search_query])
        if result['data'] == 'False' or not result['data']:
            logging.info("No data found for file {}".format(file_name))
            return []
         
        logging.info("Found {} results".format(len(result['data'])))
        return result['data']

    def get_best_sub(self, movie_file):
        file_root, movie_ext = os.path.splitext(movie_file)

        if any(map(os.path.exists, 
                   (file_root + '.' + subext for subext in STYPES))):
             logging.warning("Subtitle exists for movie {}".format(
                 os.path.basename(movie_file)))
             print "Subtitle exists for movie {}".format(
                 os.path.basename(movie_file))

             return None

        results = self.get_subs(movie_file)
        if not results:
            return None

        self.sorter.movie, _ = os.path.splitext(os.path.basename(movie_file))
        best = min(results, key=self.sorter.bestfn)
        
        print "Found subtitle in {lang} for movie {mn}:\n {link} => {d}"\
             .format(lang=best['LanguageName'], mn=best['MovieName'],
                     link=best['SubDownloadLink'], 
                     d=file_root + '.' + best['SubFormat'])

        file_name = file_root + '.' + best['SubFormat'] 

        with open(file_name, 'w') as subfile:
            gzsub = urllib2.urlopen(best['SubDownloadLink'])
            subfile.write(zlib.decompress(gzsub.read(), 16+zlib.MAX_WBITS))
        return file_name


