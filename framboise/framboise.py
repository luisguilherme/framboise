import argparse
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

def is_video(vfile):
    return os.path.splitext(vfile)[1][1:] in VTYPES

def main(argv=None):
    if argv is None:
        argv = sys.argv
    
    parser = argparse.ArgumentParser(description='Download subtitles from '
                                         'opensubtitles.org')
    parser.add_argument('locations', metavar='file or dir', type=str,
                        nargs='+', help='files or dirs you want to scan '
                        'in order to find subtitles')
    parser.add_argument('--langs', '-l', dest='langs', nargs=1,
                        default='all', metavar='lang1[,lang2,...]',
                        help='comma separated list of languages to search '
                        'sorted most preferred to least preferred')
    parser.add_argument('--no-recursive', dest='norec', 
                        action='store_const', const=True, default=False,
                        help='do not search recursively for files')
    parser.add_argument('--overwrite', '-O', dest='overwrite',
                        action='store_const', const=True, default=False,
                        help='overwrite existing subtitles')
    parser.add_argument('--save-all', action='store_const', dest='save_all',
                        const=True, default=False,
                        help='save subtitles for all langs found')
    parser.add_argument('--get-other', '-g', action='store_const', 
                        dest='get_other',
                        const=True, default=False,
                        help='get other (or same) languages for subtitle even '
                        'if there is already subtitles found')
    parser.add_argument('--ignore-names', '-I', action='store_const', 
                        dest='ignore_names', const=True, 
                        default=False,
                        help='ignore server subtitle name when searching for '
                        'best subtitle')

    args = parser.parse_args()
            
    files = []
    for location in args.locations:
        if os.path.isdir(location):
            if args.norec:
                files.extend(os.path.join(location, f) for f in
                             os.listdir(location) if is_video(f))
                
            else:
                files.extend(os.path.join(p, f) for p,fl in
                             imap(itemgetter(0,2), os.walk(location)) 
                             for f in fl if is_video(f))
        else:
            files.append(location)
            
    print files
    sorter = DefaultSorter if args.ignore_names \
             else SimilaritySorter(args.langs)
    downloader = Downloader(args.langs, sorter=sorter, 
                            overwrite=args.overwrite, save_all=args.save_all,
                            get_other=args.get_other)
    for movie_file in files:
        downloader.get_best_sub(movie_file)

if __name__ == '__main__':
    main(sys.argv)

