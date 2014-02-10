import warnings
import requests
import hashlib
import time

from bs4 import BeautifulSoup

class BremenDeRss(object):
    def __init__(self, target=None):
        self.target=target

    def parse(self, entry):
        # print entry
        key = hashlib.sha1(str("%s%s" % (entry['published'],entry['link']))).hexdigest()
        if not key in self.target.keys():

            print("new advert from %s: %s" % (entry['published'], entry['title_detail']['value']))

            self.target[key] = dict()

            self.target[key]['date'] = entry['published_parsed']
            self.target[key]['title'] = entry['title_detail']['value']
            self.target[key]['text'] = entry['summary_detail']['value']

            self.target[key]['score'] = 0
            self.target[key]['url'] = entry['link']

            self.target[key]['lastfetched'] = time.time()
            self.target[key]['lastranked'] = None

            self.target[key]['detector'] = "BremenDeRss"

        return key


class BremenDeFullText(BremenDeRss):
    def __init__(self, target=None):
        super(BremenDeFullText, self).__init__(target)


    def parse(self, entry):
        key = super(BremenDeFullText, self).parse(entry)

        if self.target[key]['detector'] != "BremenDeFullText":

            # print(">> query for full text at %s (prev. parsed by %s)" % (self.target[key]['url'], self.target[key]['detector']))
            page = requests.get(self.target[key]['url'])

            # manually cut out the interesting section
            soup = BeautifulSoup(page.text)
            tag = soup.find(id="freie_anzeige")
            if tag is None:
                tag = soup.find(id="gewerbliche_anzeige")
            if tag is None:
                warnings.warn("no freie_anzeige or gewerbliche_anzeige in entry!")
            par = tag.findAll('p')
            if len(par) != 3:
                self.target[key]['text'] = tag.text
            else:
                self.target[key]['text'] = par[2].text

            self.target[key]['detector'] = "BremenDeFullText"

            # print self.target[key]

        return key