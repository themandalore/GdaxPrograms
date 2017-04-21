'''Machine Learning program to figure out how to trade'''

'''
fees -- kraken (maker - .16% , taker .26%)
		btce (.2% fee)
		coinbase (maker fee - 0%, taker .25%)

'''

#TAKE OUT difs from dif datasets!!!!!

from sklearn import svm,preprocessing
from pandas import *
import pandas as pd
import numpy as np
from numpy import array
import os,glob
from stored import *

version = 'v5'
inc_vers = ('v5',)

directory = 'C:\\Code\\btc\\Trader\\Data\\'
'''
Use prices.csv when ready
'''

classified =version+"_total.csv"
exchange = 'kraken'

numby= 0
px = 0
nlen = 0
os.chdir(directory)
for v in inc_vers:
	for file in glob.glob(v+"_*.csv"):
		numby = numby +1
		dfname='df_'+str(numby)
		dfname = pd.DataFrame.from_csv(file)
		dfname= dfname[dfname['K_bid'] > -1]
		#dfname.reset_index()
		dfname,kpx,cbpx = preprocess(dfname)
		if exchange =='kraken':
			px1=kpx
		elif exchange=='coinbase':
			px1=cbpx
		px = px1 + px
		nlen = nlen + len(dfname.index)
		if numby == 1:
			dfone = dfname
			print('Base:',file)
		else:
			dfone = dfone.append(dfname,ignore_index=True)
			print (len(dfname.index))
			print (len(dfone.index))
			print ('Appended:',file)

    	
dfone.to_csv(directory+'total_'+classified)
print (len(dfone.index))
dfone['k_time2'] = pd.to_datetime(dfone['k_time'])
dfone['timechange']=dfone['k_time2'] - dfone['k_time2'].shift(1)
#print (dfone.head())
dfone = dfone.drop(dfone[dfone['timechange'] > Timedelta('0 days 00:02:00')].index)
dfone = dfone.drop(dfone[dfone['timechange'] < Timedelta('0 days 00:00:01')].index)
dfone = dfone.drop(dfone[dfone['ma_diff20'] == 0].index)
df=dfone.drop('k_time',1)
df=df.drop('timechange',1)
#df=df.drop('k_time2',1)
#df = df.replace("NaN",-99999).replace("N/A",-99999).replace('NaT',-999999)


#data_dfc = df.reset_index()
print (df.head())
print (len(df.index))

'''
Buy lowest, sell highest exchange

data_dfc['buy_ex'] = data_dfc.apply(lambda x : 'btce' if  x['k_ask'] > x['btce_ETH_buy'] else 'k',axis = 1)
data_dfc['lowest_buy'] = data_dfc.apply(lambda x : x['btce_ETH_buy'] if  x['k_ask'] > x['btce_ETH_buy'] else x['k_ask'],axis = 1)
data_dfc['bfee'] = data_dfc.apply(lambda x : .002 if  x['k_ask'] > x['btce_ETH_buy'] else .0016 ,axis = 1)

data_dfc['sell_ex'] = data_dfc.apply(lambda x : 'btce' if x['K_bid'] < x['btce_ETH_sell'] else 'k',axis = 1)
data_dfc['highest_sell'] = data_dfc.apply(lambda x : x['btce_ETH_sell'] if x['K_bid'] < x['btce_ETH_sell']  else x['K_bid'],axis = 1)
data_dfc['sfee'] = data_dfc.apply(lambda x : .002 if  x['K_bid'] < x['btce_ETH_sell'] else .0016 ,axis = 1)

data_dfc['cx_profit'] = quantity * data_dfc['highest_sell'] - data_dfc['highest_sell'] * data_dfc['sfee'] - data_dfc['lowest_buy']*data_dfc['bfee'] - data_dfc['lowest_buy']* quantity

data_dfc['action'] = data_dfc.apply(lambda x : 'None' if  x['cx_profit'] <= 0 else str('Buy at'+ data_dfc['buy_ex'] + 'and Sell at:' + data_dfc['sell_ex']) ,axis = 1)
'''

'''
Capture Spread on exchange

data_dfc['sp_k_profit'] = data_dfc['k_spread'] * quantity - (.0032 * quantity * data_dfc['k_spread'] )
data_dfc['sp_btce_profit'] = data_dfc['btce_spread'] * quantity - (.0032 * quantity * data_dfc['btce_spread'] )
'''

print (df.head())
print ('profit opps =',px)
print ('Input length:',nlen)
print ('Output length:', len(df.index))
df.to_csv(directory+'p_'+classified)

