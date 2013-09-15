from itertools import imap
from operator import itemgetter
import os
import sys

from opensubtitles import Downloader
from sorting import DefaultSorter, SimilaritySorter

VTYPES = ['3g2', '3gp', '3gp2', '3gpp', '60d', 'ajp', 'asf', 'asx', 'avchd', 
          'avi', 'bik', 'bix', 'box', 'cam', 'dat', 'divx', 'dmf', 'dv', 
          'dvr-ms', 'evo', 'flc', 'fli', 'flic', 'flv', 'flx', 'gvi', 'gvp', 
          'h264', 'm1v', 'm2p', 'm2ts', 'm2v', 'm4e', 'm4v', 'mjp', 'mjpeg', 
          'mjpg', 'mkv', 'moov', 'mov', 'movhd', 'movie', 'movx', 'mp4', 
          'mpe', 'mpeg', 'mpg', 'mpv', 'mpv2', 'mxf', 'nsv', 'nut', 'ogg', 
          'ogm', 'omf', 'ps', 'qt', 'ram', 'rm', 'rmvb', 'swf', 'ts', 'vfw', 
          'vid', 'video', 'viv', 'vivo', 'vob', 'vro', 'wm', 'wmv', 'wmx', 
          'wrap', 'wvx', 'wx', 'x264', 'xvid']

def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    spath = argv[1]
    langs = argv[2]
    
    files = [os.path.join(p, f) for p,fl in 
             imap(itemgetter(0,2), os.walk(spath))
             for f in fl if f.split('.')[-1] in VTYPES]
    
    downloader = Downloader(langs, sorter=SimilaritySorter(langs))
    for movie_file in files:
        downloader.get_best_sub(movie_file)

if __name__ == '__main__':
    main(sys.argv)

