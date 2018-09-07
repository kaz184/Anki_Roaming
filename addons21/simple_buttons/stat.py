import json
from bisect import bisect_left
import math
from aqt.utils import showInfo
from os import path

DATA_FILE = path.join(path.dirname(__file__), 'stat.json')

class _Stat:
    # data := [(timeTaken, count),*]
    data = None

    # after `halflife` times you've answered, all count must be a half of original.
    # this determines how fast the stats changes by your answers.
    halflife = None


    def __init__(self, halflife=100):
        self.halflife = halflife
        self.load()


    def load(self):
        try:
            with open(DATA_FILE, "r") as f:
                self.data = json.loads(f.read())
        except:
            self.data = {}

        if not isinstance(self.data, dict):
            self.data = {}


    def save(self):
        with open(DATA_FILE, "w") as f:
            f.write(json.dumps(self.data))
            f.flush()


    def keep_invariant(self, id_):
        data = self.data.get(id_, [])
        data.sort(key=lambda x:x[0])
        self.data[id_] = data


    def timeTakens(self, id_):
        return [ d[0] for d in self.data[id_] ]


    def counts(self, id_):
        return [ d[1] for d in self.data[id_] ]


    def cumulative_counts(self, id_):
        ret = []
        acc = 0
        for c in self.counts(id_):
            acc += c
            ret.append(acc)
        return ret



    def add(self, id_, timeTaken):
        self.keep_invariant(id_)

        decay = 1 - math.log(2) / self.halflife
        timeTaken = round(timeTaken, 1) # this make #self.data feasible for pure Python

        timeTakens = self.timeTakens(id_)
        counts = [ decay * c for c in self.counts(id_) ]

        idx = bisect_left(timeTakens, timeTaken)
        N = len(counts)
        equalTime = lambda x: abs(x - timeTaken) < 1e-2 # equality for float
        if idx < N:
            if N > 0 and equalTime(timeTakens[idx]):
                counts[idx] += 1
            else:
                counts.insert(idx, 1)
                timeTakens.insert(idx, timeTaken)
        else:
            if N > 0 and equalTime(timeTakens[-1]):
                # just count
                counts[-1] += 1
            else:
                # append new one to both
                counts.append(1)
                timeTakens.append(timeTaken)

        self.data[id_] = list(zip(timeTakens, counts))


    def quantile(self, id_, timeTaken): # id -> float -> float
        self.keep_invariant(id_)

        timeTakens = self.timeTakens(id_)
        c_counts = self.cumulative_counts(id_)
        
        idx = bisect_left(timeTakens, timeTaken)

        N = len(c_counts)
        return 0.0                          if N < 1   \
        else   c_counts[idx] / c_counts[-1] if idx < N \
        else   1.0


Stat = _Stat()
