'''
    Get files from ExchangeRate and TAIEX folders,
    then convert into DataFrame and Visualization
        
    @author: Double
'''
from fullCrawler_TAIEX import dir_TAIEX
from fullCrawler_FX import dir_FX
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fontMan
import pandas as pd
import os
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.font_manager import FontProperties
from _datetime import datetime

# Get fileNames from folders
def getfileNames(dir, list, removeObj):
    for dirPath, dirNames, fileNames in os.walk('./'+dir+'/'):
        for f in fileNames:
            list.append(f.rstrip(removeObj))
    return list        
    

# Create a directory if that doesn't exist
def makedir (directory):
    if not os.path.isdir(directory):
        os.makedirs (directory)


print('--------------------------START Visualization--------------------------')
# Read TAIEX files with CSV format from folder and convert into DataFrame
URL_TAIEXs = []
remove_TAIEX = '.csv'
getfileNames(dir_TAIEX, URL_TAIEXs, remove_TAIEX)

TAIEX_pd = []
for URL_T in URL_TAIEXs:
    TAIEX_W = pd.read_csv(dir_TAIEX+'/'+URL_T+remove_TAIEX, encoding='big5', header=1, skipfooter=3, engine='python')
    TAIEX_pd.append(TAIEX_W)

# TAIEX Data Clean
TAIEX_pd =  pd.concat(TAIEX_pd, axis=0, ignore_index=True)
TAIEX_pd['日期'] = pd.to_datetime(TAIEX_pd['日期'])
TAIEX_pd['發行量加權股價指數'] = TAIEX_pd['發行量加權股價指數'].str.replace(',', '').astype(float)
TAIEX_pd['成交股數'] = ((TAIEX_pd['成交股數'].str.replace(',', '').astype(float))/1000)/1000000     # Volume: 成交量百萬張
TAIEX_pd['成交金額'] = (TAIEX_pd['成交金額'].str.replace(',', '').astype(float))/100000000          # Turnover: 成交金額億元
TAIEX_pd = TAIEX_pd.sort_values(by='日期', ascending=True).reset_index(drop=True)
TAIEX_pd.set_index('日期')

# Read FX files with JSON format from folder and convert into DataFrame
URL_Curs = []
remove_Cur = '6m.json'
getfileNames(dir_FX, URL_Curs, remove_Cur)

for URL_C in URL_Curs:    
    with open(dir_FX+'/'+URL_C+remove_Cur, 'r', encoding='utf-8') as FX_input:
        FX6m_W = json.load(FX_input)
        FX6m_Data = FX6m_W[0]['data']
        
        # FX Data Clean
        FX6m_pd = pd.DataFrame(FX6m_Data, columns=['Date', 'Cash_Bid', 'Cash_Ask', 'Spot_Bid', 'Spot_Ask'])             
        FX6m_pd['Date'] = pd.to_datetime(FX6m_pd['Date'])
        FX6m_pd[['Spot_Bid', 'Spot_Ask']] = FX6m_pd[['Spot_Bid', 'Spot_Ask']].astype(float)
        FX6m_pd = FX6m_pd.sort_values(by='Date', ascending=True).reset_index(drop=True)
        FX6m_pd.set_index('Date')
        
        # Adjust the Dataframe of TAIEX to make its length equal to Dataframe of FX
        len_differ = len(TAIEX_pd) - len(FX6m_pd)
        TAIEX_pdAdj = TAIEX_pd.iloc[len_differ: , :].reset_index(drop=True)

        # Plot Figure
        fig = plt.figure(figsize=(10, 8))
 
        # Plot 1: TAIEX
        ax0 = fig.add_subplot(3,1,1)
        ax0.plot(TAIEX_pdAdj['日期'], TAIEX_pdAdj['發行量加權股價指數'], color='red', label='TAIEX')
           
        fontP = fontMan.FontProperties()
        fontP.set_family('Microsoft JhengHei')
        fontP.set_size(14)
        ax0.set_title('台灣加權股價指數（TAIEX）', FontProperties=fontP)
        ax0.legend()
           
        # Plot 2: Volume and Turnover
        ax1 = fig.add_subplot(3,1,2)
        ax1_1 = ax1.twinx()
        ax1bar = ax1.bar(TAIEX_pdAdj['日期'], TAIEX_pdAdj['成交股數'], color='#BEBEBE', label='Volume', width=0.5)
        ax1_1plot, = ax1_1.plot(TAIEX_pdAdj['日期'], TAIEX_pdAdj['成交金額'], color='#00BB00', label='Turnover')
           
        ax1.grid(True, linestyle='-.', color='#E0E0E0')
        ax1.yaxis.tick_right()
        ax1.set_ylabel('百萬張')
        ax1.yaxis.set_label_position('right')
        ax1_1.yaxis.tick_left()
        ax1_1.set_ylabel('億元')
        ax1_1.yaxis.set_label_position('left')
        ax1.set_title('市場成交量（Volume） vs 成交金額（Turnover）', FontProperties=fontP)
        labels = [ax1bar, ax1_1plot]
        ax1.legend(labels, [l.get_label() for l in labels])
 
        # Plot 3: FX
        ax2 = fig.add_subplot(3,1,3)
        # Test Date in TAIEX_pdAdj & FX6m_pd is the same or not
        for n in range(len(TAIEX_pdAdj['日期'])):
            while TAIEX_pdAdj['日期'][n] != FX6m_pd['Date'][n]:
                print('Inconsistent Date:',TAIEX_pdAdj['日期'][n],'<=>',FX6m_pd['Date'][n])
            
        ax2.plot(FX6m_pd['Date'], FX6m_pd['Spot_Bid'], color='#2894FF', label='Spot_Bid')
        ax2.plot(FX6m_pd['Date'], FX6m_pd['Spot_Ask'], color='#FF9224', label='Spot_Ask')
        ax2.grid(True, linestyle='-.', color='#E0E0E0')        
        ax2.set_title(URL_C+'/TWD', FontProperties=fontP)
        ax2.legend()
           
        # Adjust distance between Subplots
        fig.subplots_adjust(hspace = 0.33) # or fig.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)    
                   
        # Adjust the appearance of Xaxis ticker
        xmajorLocator = mdates.MonthLocator()
        xminorLocator = mdates.DayLocator()
        for ax in [ax0, ax1, ax2]:
            ax.xaxis.set_major_locator(xmajorLocator)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_minor_locator(xminorLocator)
                       
        # Save output as png 
        directory = 'Pictures'
        makedir(directory)
        fig.savefig(directory+'/TAIEXvs'+URL_C+'.png', dpi=300)
        
        # Display all figures and Cancle the block set up(if True, next figure will be shown until the previous figure has been closed.
        plt.show(block=False)
         
plt.pause(10)
plt.close()
print('--------------------------END--------------------------')    

