class parseWiki():
    
    rawData = {}
    
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

if __name__ == '__main__':

    parser = parseWiki()
    parser.processDrama('A Tale of Two Sisters')
    parser.processDrama('Can We Love Again?')

    print parser.getCast('Can We Love Again?')

