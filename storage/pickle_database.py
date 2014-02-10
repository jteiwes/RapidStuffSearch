import os
import pickle

class PickleDataBase(object):

    def __init__(self, filename):
        self.filename=filename
        self.load()

    def __getitem__(self, item):
        return self.db.__getitem__(item)

    def __setitem__(self, key, value):
        self.db.__setitem__(key, value)

    def load(self):
        if os.path.isfile(self.filename):
            self.db = pickle.load(open(self.filename, "r"))
        else:
            self.db = dict()

    def store(self):
        pickle.dump(self.db, open(self.filename, "w"))

    def keys(self):
        return self.db.keys()

    def info(self):
        return str("%d entries in database" % len(self.keys()))