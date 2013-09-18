from exceptions import StandardError
import gzip
import logging
from operator import itemgetter
import os
from subprocess import Popen, PIPE
import urllib2
import xmlrpclib
import zlib

import chksum
from sorting import DefaultSorter
from util import map_

USER_AGENT = 'framboise v0.2'
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
                 os_language='en', get_other=False, overwrite=False,
                 save_all=False):
        self.langs = langs
        self.cr_user = cr_user
        self.cr_pass = cr_pass
        self.os_language = os_language
        self.get_other = get_other
        self.overwrite = overwrite
        self.save_all = save_all
        
        self.sorter = sorter if sorter is not None else DefaultSorter(langs)
        
        self.logged_in = False
        
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

    def __exit__(self):
        if self.logged_in:
            self.server.LogOut(self.token)

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

    def save_subtitle(self, subtitle, file_root, prefix=''):
        file_name = '.'.join(
            filter(None,
                   [file_root,prefix,subtitle['SubFormat']]))

        print "Found subtitle in {lang} for movie {mn}:\n{link} =>\n    {d}"\
            .format(lang=subtitle['LanguageName'], mn=subtitle['MovieName'],
                    link=subtitle['SubDownloadLink'], 
                    d=file_name)
        
        if os.path.exists(file_name) and not self.overwrite:
            return None

        with open(file_name, 'w') as subfile:
            gzsub = urllib2.urlopen(subtitle['SubDownloadLink'])
            subfile.write(zlib.decompress(gzsub.read(), 16+zlib.MAX_WBITS))
        return file_name

    def get_best_sub(self, movie_file):
        file_root, movie_ext = os.path.splitext(movie_file)
        file_exists = False

        if any(map(os.path.exists, 
                   (file_root + '.' + subext for subext in STYPES))):
            print "Subtitle exists for movie {}".format(
                os.path.basename(movie_file))
            file_exists = True
            if not (self.overwrite or self.get_other):
                return None

        results = self.get_subs(movie_file)
        if not results:
            return None

        self.sorter.movie, _ = os.path.splitext(os.path.basename(movie_file))
        if self.save_all or self.get_other:
            lmap = map_(results, keyfn=itemgetter('SubLanguageID'))
            bestl = {k: min(lmap[k], key=self.sorter.bestfn)
                     for k in lmap}
            for lang,best in bestl.iteritems(): 
                self.save_subtitle(best, file_root, prefix=lang)
        
        best = min(results, key=self.sorter.bestfn)
        if not file_exists or self.overwrite:
            self.save_subtitle(best, file_root)
            


