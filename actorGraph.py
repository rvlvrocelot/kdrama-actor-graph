from bs4 import BeautifulSoup
import urllib
import urllib2
from pymongo import MongoClient

class ParseWiki():
    
    rawData = {}
    
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
        
        soup = BeautifulSoup(castSubSet)
        rawCast = [x.get('title') for x in soup.find_all('a')]
        for i,cast in enumerate(rawCast):
            if cast:
                if '(' in cast:
                    rawCast[i] = rawCast[i][0:cast.index('(') -1]
                
        rawCast = set(rawCast)
        
        self.rawData[name.replace('_','')]['cast'] =  rawCast
        
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
        
        monthList = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        detailsSubset = self._getBetween(html,'Details')
        soup = BeautifulSoup(detailsSubset)
        raw =  [s.get_text() for s in soup.findAll('li') if 'Broadcast period' in s.get_text()]
        if raw:
            year = raw[0][18:30][0:4]
            month = int(monthList.index(raw[0][18:30][5:8])) + 1
            if month < 10:
                month = '0' + str(month)
            day = raw[0][18:30][9:11]
                        
            finalString = year + str(month) + day
            
            self.rawData[name.replace('_','')]['startDate'] = finalString
        else:
            self.rawData[name.replace('_','')]['startDate'] = []
            
    def _processGenre(self,html,name):
        
        detailsSubset = self._getBetween(html,'Details')
        soup = BeautifulSoup(detailsSubset)
        raw =  [s.get_text() for s in soup.findAll('li') if 'Genre' in s.get_text()]
        if raw:
            self.rawData[name.replace('_','')]['genre'] = raw[0].split()[1:]
        else:
            self.rawData[name.replace('_','')]['genre'] = []
            
    def _processImage(self,html,name):
        
        soup = BeautifulSoup(html)
        if soup.findAll('img'):
            imageUrl = "http://wiki.d-addicts.com/" +  [x['src'] for x in soup.findAll('img')][0]
        else:
            imageUrl = ""
        self.rawData[name.replace('_','')]['image'] = imageUrl
        
    def _processName(self,name):
        
        self.rawData[name.replace('_','')]['name'] = name
        

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
        self._processName(name)
        
        
    def getCast(self,dramaName):
        return self.rawData[dramaName.replace(' ','')]['cast']
    
    def getSynopsis(self,dramaName):
        if not self.rawData[dramaName.replace(' ','')]['synopsis']:
            return "Synopsis not found"
        return self.rawData[dramaName.replace(' ','')]['synopsis']
    
    def getName(self,dramaName):
        return self.rawData[dramaName.replace(' ','')]['name'].replace("_"," ")
    
    def getStartDate(self,dramaName):
        if not self.rawData[dramaName.replace(' ','')]['startDate']:
            return "Start date not found"
        return self.rawData[dramaName.replace(' ','')]['startDate']
    
    def getImage(self, dramaName):
        if not self.rawData[dramaName.replace(' ','')]['image']:
            return "image not found"
        return self.rawData[dramaName.replace(' ','')]['image']
    
    def getGenre(self,dramaName):
        if not self.rawData[dramaName.replace(' ','')]['genre']:
            return ["NoGenre"]
        return self.rawData[dramaName.replace(' ','')]['genre']
    
    def initializeDB(self):
        conn = sqlite3.connect('kdramaData.db')
        c = conn.cursor()
        
        c.execute('''Drop TABLE drama''')
        c.execute('''Drop TABLE cast''')
        c.execute('''Drop TABLE genre''')
        
        c.execute('''CREATE TABLE drama
             (ID INTEGER PRIMARY KEY AUTOINCREMENT, name text, synopsis text, startDate int, image text)''')

        c.execute('''CREATE TABLE cast
             (dramaID INT, castName text)''')

        c.execute('''CREATE TABLE genre
             (dramaID INT, genreName text)''')

        conn.commit()
        conn.close()
    
    def insertDB(self,dramaName):
        conn = sqlite3.connect('kdramaData.db')
        conn.text_factory = str
        c = conn.cursor()
        
        
        #print self.getName(dramaName),self.getSynopsis(dramaName),self.getImage(dramaName), self.getStartDate(dramaName)
        c.execute('''
        
        INSERT INTO drama (name,synopsis, image, startDate )
        VALUES (?,?,?,?) 
        
        ''',(self.getName(dramaName),self.getSynopsis(dramaName),self.getImage(dramaName), self.getStartDate(dramaName) ))
        
        conn.commit()
        
        dramaIndex = c.execute(''' SELECT last_insert_rowid() ''').fetchall()[0][0]
        
        for cast in self.getCast(dramaName):
            c.execute('''
        
                INSERT INTO cast (dramaID,castName )
                VALUES (?,?) 
        
        ''',(dramaIndex,cast))
            conn.commit()
            
        #print self.getGenre(dramaName)     
        if len(self.getGenre(dramaName)) > 0:
            for genre in self.getGenre(dramaName):
                lowerGenre = genre.lower()
                c.execute('''

                    INSERT INTO genre (dramaID,genreName )
                    VALUES (?,?) 

            ''',(dramaIndex,lowerGenre))
                conn.commit()
        
        conn.close()
        
if __name__ == '__main__':
    
    parser = ParseWiki()
    
    parser.initializeDB()
    
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

    dramaList2015 = getDramaList(2015)
    dramaList2014 = getDramaList(2014)
    dramaList2013 = getDramaList(2013)
    dramaList = set(dramaList2015+dramaList2014+dramaList2013)
    for drama in dramaList:
        print drama
        parser.processDrama(drama)
        parser.insertDB(drama)
                           
