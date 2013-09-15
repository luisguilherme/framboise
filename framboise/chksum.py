import struct
import os

# CHKSUM CONFIG
BITS = 64
BYTES = BITS / 8

BUFSIZE = 1024 * 64

def os_hash(movie_file): 
    fmt = 'Q' * (BUFSIZE / BYTES)
    with open(movie_file, 'rb') as fd:
        w1 = struct.unpack(fmt, fd.read(BUFSIZE))
        fd.seek(-BUFSIZE, os.SEEK_END)
        w2 = struct.unpack(fmt, fd.read(BUFSIZE))
        return "{0:16x}".format(
            reduce(lambda a,b: (a + b) % (1 << BITS), w1 + w2) + fd.tell())

if __name__ == '__main__':
    import sys
    print "%x" % hash(sys.argv[1])
