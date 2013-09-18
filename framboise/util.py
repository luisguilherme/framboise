from collections import defaultdict

def map_(generator, keyfn):
    _map = defaultdict(list)
    for item in generator:
        _map[keyfn(item)].append(item)
    return _map

    
