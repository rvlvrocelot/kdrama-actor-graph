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
        try: 
            response = urllib2.urlopen(url)
            html = response.read()
        except:
            html = ""
        
        return html
    
    def _getBetween(self,htmlString,firstTag):
        
        try:
            html = BeautifulSoup(htmlString,from_encoding="UTF-8")
            first = html.find(id = firstTag)
            last = first.find_next('span')
            tags = ""
            iter = first
            while iter.next != last:
                #if iter.string: 
                tags += unicode(iter)
                iter = iter.next
        
        except AttributeError:
            tags = ""
        return tags
            
    
    def _processCast(self,html,name):
        
        castSubSet = self._getBetween(html,'Cast')
        
        if not castSubSet:
            self.rawData[name.replace('_','')]['cast'] = []
            return 0
        
        soup = BeautifulSoup(html)
        self.rawData[name.replace('_','')]['cast'] =  set([x.get('title') for x in soup.find_all('a')])
        
    def _processSynopsis(self,html,name):
        
        synopsisSubSet = self._getBetween(html,'Synopsis')
        
        if not synopsisSubSet:
            self.rawData[name.replace('_','')]['synopsis'] = []
            return 0
        
        soup = BeautifulSoup(synopsisSubSet)
        try:
            self.rawData[name.replace('_','')]['synopsis'] = soup.find_all('p')[0].get_text()
        except IndexError:
            self.rawData[name.replace('_','')]['synopsis'] = []
            
    def _processStartDate(self,html,name):
        
        detailsSubset = self._getBetween(html,'Details')
        soup = BeautifulSoup(detailsSubset)
        raw =  [s.get_text() for s in soup.findAll('li') if 'period' in s.get_text()]
        if raw:
            self.rawData[name.replace('_','')]['synopsis'] = raw[0][18:30]
        else:
            self.rawData[name.replace('_','')]['synopsis'] = []
            
    def _processGenre(self,html,name):
        
        detailsSubset = self._getBetween(html,'Details')
        soup = BeautifulSoup(detailsSubset)
        raw =  [s.get_text() for s in soup.findAll('li') if 'Genre' in s.get_text()]
        if raw:
            self.rawData[name.replace('_','')]['genre'] = raw[0]
        else:
            self.rawData[name.replace('_','')]['genre'] = []
            
    def _processImage(self,html,name):
        
        soup = BeautifulSoup(html)
        imageUrl = "http://wiki.d-addicts.com/" +  [x['src'] for x in soup.findAll('img')][0]
        self.rawData[name.replace('_','')]['image'] = imageUrl
        print imageUrl

    def processDrama(self,dramaName):
        
        name  = dramaName.replace(' ','_')
        html = self._download('http://wiki.d-addicts.com/' + urllib.quote_plus(name))
        
        if name.replace('_','') not in self.rawData:
            self.rawData[name.replace('_','')] = {}
        
        #process cast
        self._processCast(html,name)
        self._processSynopsis(html,name)
        self._processStartDate(html,name)
        self._processGenre(html,name)
        self._processImage(html,name)
        
        
    def getCast(self,dramaName):
        return self.rawData[dramaName.replace(' ','')]['cast']
    
    def getSynopsis(self,dramaName):
        return self.rawData[dramaName.replace(' ','')]['synopsis']
    
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
    def getDramaList(year):
            html = parser._download("http://wiki.d-addicts.com/List_of_Dramas_aired_in_Korea_by_Network_in_" + str(year))
            soup = BeautifulSoup(html)
            rawList = [x.get('title') for x in soup.find_all('a')]
            endString = "List of Dramas aired in Korea by Network in " + str(year -1)
            finalList = [x for x in rawList if x]
            finalList = finalList[0:finalList.index(endString)]
            finalList = [x.encode("utf8") for x in finalList]
            for i,x in enumerate(finalList):
                if '(' in x:
                    finalList[i] = x[0:x.index('(') -1]
                
            return finalList

    dramaList = getDramaList(2014)
    for drama in dramaList:
        print drama
        parser.processDrama(drama)


    parser.drop()

    #parser.save('Bad Couple')

    parser.recover()

