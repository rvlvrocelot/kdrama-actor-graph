from bs4 import BeautifulSoup
import urllib
import urllib2
from pymongo import MongoClient

class ParseWiki():
    
    rawData = {}
    client = MongoClient()
    drama = client.db.drama
    
    def __init__(self):
        pass
    
    def _download(self,url):
        response = urllib2.urlopen(url)
        html = response.read()
        return html
    
    def _getBetween(self,htmlString,firstTag):
        
        html = BeautifulSoup(htmlString,from_encoding="UTF-8")
        first = html.find(id = firstTag)
        last = first.find_next('span')
        tags = ""
        iter = first
        while iter.next != last:
            if iter.string: tags += unicode(iter)
            iter = iter.next
        return tags       
        
        
    def processDrama(self,dramaName):
        
        name  = dramaName.replace(' ','_')
        html = self._download('http://wiki.d-addicts.com/' + urllib.quote_plus(name))
        
        if name.replace('_','') not in self.rawData:
            self.rawData[name.replace('_','')] = {}
        
        #process cast
        castSubSet = self._getBetween(html,'Cast')
        soup = BeautifulSoup(castSubSet)
        self.rawData[name.replace('_','')]['cast'] =  [x.get('title') for x in soup.find_all('a')]
        
    def getCast(self,dramaName):
        return self.rawData[dramaName.replace(' ','')]['cast']
    
    def save(self,dramaName):
        name = dramaName.replace(' ','')
        entry =  self.rawData[name]
        entry['name'] = name
        return self.drama.insert_one(entry).inserted_id
    
    def recover(self):
        for x in self.drama.find():
            print x
    
    def drop(self):
        self.drama.drop()
        

if __name__ == '__main__':

    parser = ParseWiki()
    parser.processDrama('Bad Couple')
    parser.processDrama('Can We Love Again?')


    parser.drop()

    parser.save('Bad Couple')

    parser.recover()

