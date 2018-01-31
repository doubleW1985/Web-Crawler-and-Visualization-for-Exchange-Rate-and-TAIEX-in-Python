'''
    Crawling Exchange Rate from BOT and write into JSON format

    http://rate.bot.com.tw/xrt/quote/l6m/USD
    http://rate.bot.com.tw/xrt/quote/yyyy-mm-dd/USD/spot（for Intraday）

    @author: Double
'''
import requests
import time
from bs4 import BeautifulSoup
import os
import json

def get_web_page(url):
    time.sleep(2) # sleep 2s first
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


def get_contents(dom):
    soup = BeautifulSoup(dom, 'html.parser')
    outputs = []
    
    # Get period, currency, and title information
    infos = soup.find_all('div', 'chart-key-value')
    period = infos[0].find('div', 'value').string  
    currency = infos[1].find('div', 'value').text.strip()   
    title = infos[2].find('div', 'value').string.replace("本行", "臺灣銀行近半年")   # replace original wording
    
    # Get table title
    FXtable = soup.find('table', 'table table-striped table-bordered table-condensed table-hover')
    FXtableTrinTH = FXtable.find('thead').find_all('tr')
    date = FXtableTrinTH[0].find('th', 'noscript').string
    cash_Bid = '現金'+FXtableTrinTH[1].find_all('th')[0].string.lstrip('本行')
    cash_Ask = '現金'+FXtableTrinTH[1].find_all('th')[1].string.lstrip('本行')
    spot_Bid = '即期'+FXtableTrinTH[1].find_all('th')[2].string.lstrip('本行')
    spot_Ask = '即期'+FXtableTrinTH[1].find_all('th')[3].string.lstrip('本行')
    
    # Get quote information
    FXdata = []
    FXtableTrinTB = FXtable.find('tbody').find_all('tr')
    for data in FXtableTrinTB:
        QuoteDate = data.find_all('td')[0].string
        QuoteCash_Bid = data.find_all('td')[2].string
        QuoteCash_Ask = data.find_all('td')[3].string
        QuoteSpot_Bid = data.find_all('td')[4].string
        QuoteSpot_Ask = data.find_all('td')[5].string
        FXdata.append([QuoteDate, QuoteCash_Bid, QuoteCash_Ask, QuoteSpot_Bid, QuoteSpot_Ask])

    # Summary     
    outputs.append({
        'title' : title,
        'currency' : currency,
        'period' : period,
        'fields' : [date, cash_Bid, cash_Ask, spot_Bid, spot_Ask],
        'data' : FXdata
        })
    return outputs


# Create a directory if that doesn't exist
def makedir(directory):
    if not os.path.isdir(directory):
        os.makedirs (directory)


print('--------------------------START Crawling Exchange Rate--------------------------')
# Set Currency would query
URL_Curs = ['USD', 'JPY', 'CNY']

# Crawl Beginning
for URL_Cur in URL_Curs:
    URL_6mFX = 'http://rate.bot.com.tw/xrt/quote/l6m/'
    FX_6m = get_web_page(URL_6mFX + URL_Cur)
    if FX_6m:
        result = get_contents(FX_6m)
        
        # Set directory and filename
        dir_FX = 'ExchangeRate'
        fname_FX = '/'+URL_Cur+'6m.json'
        makedir(dir_FX)
        
        # Write into JSON
        with open(dir_FX + fname_FX, 'w', encoding='utf-8') as res:
            json.dump(result, res, indent=2, sort_keys=False, ensure_ascii=False)
print('--------------------------END--------------------------')
            
