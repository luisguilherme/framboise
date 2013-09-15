from collections import Counter
import logging

class DefaultSorter(object):
    def __init__(self, langs='all', weight=1):
        print "Available languages: ", langs
        self.langs = langs.split(',')
 
    def bestfn(self, subentry):
        idx = self.langs.index(subentry['SubLanguageID'])
        value = idx if idx >= 0 else len(self.langs)
        return value


def _similarity(a, b):
    make_pairs = lambda l: (l[i:i+1] for i in xrange(len(l)-1))
    tc = lambda counter: sum(count for count in counter.values())
    sa = Counter(make_pairs(a))
    sb = Counter(make_pairs(b))
    return 2.0 * tc(sa & sb) / (tc(sa) + tc(sb))

class SimilaritySorter(DefaultSorter):
    def __init__(self, langs='all'):
        super(SimilaritySorter, self).__init__(langs)
        self.movie = ''

    def bestfn(self, subentry):
        value = super(SimilaritySorter, self).bestfn(subentry)
        sn = subentry['SubFileName']
        similarity = _similarity(sn[:sn.rindex('.')], self.movie)
        logging.info("{}: Similarity is {}, lang {}".format(
            subentry['SubFileName'], similarity, subentry['SubLanguageID']))
        return 1.1 * value + 1 - similarity