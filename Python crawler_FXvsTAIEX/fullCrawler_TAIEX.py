'''
    Crawling Stock Market information from TWSE and write into CSV format

    http://www.twse.com.tw/exchangeReport/FMTQIK?response=html&date=yyyymmdd
    Data start from 1990/01/04
    
    @author: Double
'''
import requests
import time
from bs4 import BeautifulSoup
import os
import csv

def get_web_page(url):
    time.sleep(5) # sleep 5s first
    try:
        resp = requests.get(url=url,)
        if resp.status_code != 200:
            print('Invalid url:', resp.url)
            return None
        else:
            return resp.text
    except requests.exceptions.ConnectionError:
        requests.status_codes = "Connection refused"
        print(requests.status_codes)
        

def get_contents(dom, year):
    soup = BeautifulSoup(dom, 'html.parser') 
    outputs = []
    
    # Get table, thead, and tbody
    TAIEXtable = soup.find('table')
    TAIEXtableTrinTH = TAIEXtable.find('thead').find_all('tr')
    TAIEXtableTrinTB = TAIEXtable.find('tbody').find_all('tr')
    
    # Verify Year of Table and QuoteDate is correct or not.
    # If Yes => Get Data
    # If Not => Show Message
    Title = TAIEXtableTrinTH[0].find('th').find('div').string    
    year_adj = str(year-1911)
    KeyinYear = Title.find(year_adj)
    if KeyinYear != -1:
        replaced_Y = Title[:KeyinYear + len(year_adj)]
        
        # Get table title
        Title_adj = Title.replace(str(replaced_Y), str(year))
        Date = TAIEXtableTrinTH[1].find_all('td')[0].string
        Share = TAIEXtableTrinTH[1].find_all('td')[1].string
        Amount = TAIEXtableTrinTH[1].find_all('td')[2].string
        Count = TAIEXtableTrinTH[1].find_all('td')[3].string
        Index = TAIEXtableTrinTH[1].find_all('td')[4].string
        UpDown = TAIEXtableTrinTH[1].find_all('td')[5].string
        
        # Get quote information
        TAIEXdata = []
        for data in TAIEXtableTrinTB:
            QuoteDate = data.find_all('td')[0].string
            KeyinDate = QuoteDate.find(year_adj)
            if KeyinDate != -1:
                replaced_D = QuoteDate[:KeyinDate + len(year_adj)]
            
                QuoteDate_adj = QuoteDate.replace(str(replaced_D), str(year))
                QuoteShare = data.find_all('td')[1].string
                QuoteAmount = data.find_all('td')[2].string
                QuoteCount = data.find_all('td')[3].string
                QuoteIndex = data.find_all('td')[4].string
                QuoteUpDown = data.find_all('td')[5].string
                TAIEXdata.append([QuoteDate_adj, QuoteShare, QuoteAmount, QuoteCount, QuoteIndex, QuoteUpDown])     
            else:
                print('System Data Error in QuoteDate!!!')
                break
    else:
        print('System Data Error in Title!!!')
    
    # Get Notes
    TAIEXNotes = soup.find('div', 'notes')
    NotesTitle = TAIEXNotes.find('b').string
    NotesText1 = TAIEXNotes.find('ol').find_all('li')[0].string
    NotesText2 = TAIEXNotes.find('ol').find_all('li')[1].text
    TAIEXNotesG = [NotesTitle, NotesText1, NotesText2]
   
    # Summary
    outputs.append({
        'title' : Title_adj,
        'fields' : [Date, Share, Amount, Count, Index, UpDown],
        'data' : TAIEXdata,
        'notes' : TAIEXNotesG
    })
    return outputs    


# Create a directory if that doesn't exist
def makedir(directory):
    if not os.path.isdir(directory):
        os.makedirs (directory)


def WriteIntoCSV(result, directory, filename):
    TAIEXFile = directory + filename
    OutputFile = open(TAIEXFile, 'w', newline='')
    OutputWriter = csv.writer(OutputFile)
    CSVtitle = ''.join(result[0]['title'])
    head = [CSVtitle, '']
    OutputWriter.writerow(head)
    OutputWriter.writerow(result[0]['fields'])
    for child in (result[0]['data']):
        OutputWriter.writerow(child)
    OutputWriter.writerow([result[0]['notes'][0], ''])
    OutputWriter.writerow([result[0]['notes'][1], ''])
    OutputWriter.writerow([result[0]['notes'][2], ''])
    OutputFile.close()    


print('--------------------------START Crawling Stock Market--------------------------')
# Set Year, Month, and Date would query
URL_YMDs = ['2018-1-1', '2017-12-31', '2017-11-1', '2017-10-1', '2017-9-1', '2017-8-1', '2017-7-1']
 
# Get current Year, Month, and Date
now = time.strftime("%Y%m%d")
 
for URL_YMD in URL_YMDs:
    # Formating Year, Month, and Date would query
    YMD = URL_YMD.split('-')
    URL_YYYY = str(YMD[0])
    URL_MM = "{0:0=2d}".format(int(YMD[1]))
    URL_DD = "{0:0=2d}".format(int(YMD[2]))
    QueryYMD = URL_YYYY + URL_MM + URL_DD
        
    # Crawl Beginning
    if ( int(QueryYMD) > int(now) or int(QueryYMD) < 19900101):
        print(QueryYMD + '超出查詢範圍，請重新查詢！（查詢期間：1990/01/04至' + time.strftime("%Y/%m/%d") + '）')
    else: 
        URL_TAIEX = 'http://www.twse.com.tw/exchangeReport/FMTQIK?response=html&date='
        TAIEX_Monthly = get_web_page(URL_TAIEX + QueryYMD)
        if TAIEX_Monthly:
            year = int(URL_YYYY)
            result = get_contents(TAIEX_Monthly, year)
                 
            # Set directory and filename
            dir_TAIEX = 'TAIEX'
            fname_TAIEX = '/'+URL_YYYY+URL_MM+'.csv'
            makedir(dir_TAIEX)
                 
            # Write into CSV
            WriteIntoCSV(result, dir_TAIEX, fname_TAIEX)
print('--------------------------END--------------------------')      