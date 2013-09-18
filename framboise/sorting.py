from collections import Counter
import logging

def find(list, value):
    try: 
        return list.index(value)
    except ValueError:
        return None
        
class DefaultSorter(object):
    def __init__(self, langs='all', weight=1):
        logging.info("Available languages: {}".format(langs))
        self.langs = langs.split(',')
 
    def bestfn(self, subentry):
        idx = find(self.langs, subentry['SubLanguageID'])
        value = idx if idx is not None else len(self.langs)
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
