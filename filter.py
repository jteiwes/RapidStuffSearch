#!/usr/bin/env python
# coding: utf8

import yaml
import os
import sys
import time
import pickle
import feedparser

from detection.bremen_de import *
from storage.pickle_database import *


class Filter(object):
    def __init__(self, config_file_name, interval_m=15):
        config = yaml.load(open(config_file_name, "r"))

        if (config is None) or (not isinstance(config, dict)):
            raise Exception, str("could not read config file [%s]" % config_file_name)
        if 'feedurl' not in config.keys():
            raise Exception, "config file does not contain feedurl key!"
        if 'database' not in config.keys():
            raise Exception, "config file does not contain database filename!"

        self.config = config

        if 'threshold' not in self.config.keys():
            self.config['threshold'] = 50
            print("## no threshold for ranking given in config!")
            print("## Using default value %d" % self.config['threshold'])

        self.feedcontent = None
        self.database = PickleDataBase(self.config['database'])
        self.datadetector = BremenDeFullText(target=self.database)

        # fetch feed and rank unranked entries
        self.update()


    def update(self):
        if self.feedcontent is not None:
            self.store()
        # if we have a new database put the config entry in
        if not 'config' in self.database.keys():
            self.database['config'] = hashlib.md5(str(self.config)).hexdigest()
        # if the config file has changed rerank all entries in database
        if hashlib.md5(str(self.config)).hexdigest() != self.database['config']:
            self.rank_all()

        if os.path.exists("debug_feedcontent.pickle"):
            # setting for development, so that we don't need to poll bremen.de's site all the time
            print(">> loading feed from local file..")
            self.feedcontent = pickle.load(open("debug_feedcontent.pickle", "r"))
        else:
            self.feedcontent = feedparser.parse(self.config['feedurl'])

        for e in self.feedcontent['entries']:
            key = self.datadetector.parse(e)
            self.rank_single(key)

    def store(self):
        """creates a backup so that we can start there
        the next time this application is launched"""
        pickle.dump(self.feedcontent, open("last_feedcontent.pickle", "w"))
        self.database.store()


    def rank_all(self):
        """function to re-calculte the score value for every
        known entry in our database"""
        for key in self.database.keys():
            self.rank_single(key, rerank=True)


    def rank_single(self, key, rerank=False):
        """ function to calculate the score value"""
        e = self.database[key]

        if e['lastranked'] is not None and not rerank:
            # nothing to do here..
            return e

        print(">> ranking advert from %s: %s" % (time.asctime(e['date']), e['title']))

        self.database[key]['score'] =  0


        score = 0
        keywords = self.config['keywords']
        for sets in keywords:
            op = sets['operator'].lower()
            reward = int(sets['score'])
            factor = 0

            ltext = e['title'].lower() + " " + e['text'].lower()

            if op not in ["and"]:
                # the OR and NOT case
                if any(word in ltext for word in sets['words']):
                    for word in sets['words']:
                        factor += ltext.count(word)
                    if op in ["or"]:
                        factor = factor * 1
                    else:
                        factor = factor * (-1)
            else :
                # the AND case
                if all(word in ltext for word in sets['words']):
                    for word in sets['words']:
                        factor += ltext.count(word)

            delta = factor*reward
            score += delta

        print(">> got %d for %s" % (score, e['title']))

        self.database[key]['score'] = score
        self.database[key]['lastranked'] = time.time()


    def print_list(self, threshold=None):
        """ print out a list of entries ranked higher or equal for a given threshold
        """
        if threshold is None:
            threshold = self.config['threshold']
        sortarray = list()

        def score_sort(a, b):
            return b[1]-a[1]

        for key in self.database.keys():
            if key == 'config':
                continue
            sortarray.append((key, self.database[key]['score']))

        sortarray.sort(cmp=score_sort)

        for key, score in sortarray:
            if threshold is not None and self.database[key]['score'] < threshold:
                break
            print self.database[key]['score']
            print self.database[key]['title']
            print self.database[key]['text']
            print self.database[key]['url']
            print "-"*20


    def get_html(self):
        raise NotImplementedError


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(">> please give path to config-file as first argument!")
        exit(0)


    f = Filter(sys.argv[1])
    f.print_list()
    f.store()
