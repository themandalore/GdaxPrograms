'''market maker program'''

from transact_cb import *
from stored import *
import numpy as np
from numpy import array
import json, requests, csv, datetime
import pandas as pd
import pickle
import time
'''
Get ma quantity to replace 0 as base quantity
Get orig_price of asset to calculate profit and loss based on total value and totalvalue vs market value (if mkt loses)


'''
def getProductHistoricRates(product='', start='', end='', granularity=''):
	payload = { "start" : start, "end" : end,"granularity" : granularity}
	response = requests.get("https://api.gdax.com" + '/products/%s/candles' % (product), params=payload)
	return response.json()

class Slave1:
	def __init__(self):
		self = self
		pass

	def preprocessing(self,base,timein,granul):
		titles = ['time','low','high','open','close','volume']
		today = datetime.datetime.now().replace(second=0).replace(microsecond=0)
		dname = 'C:\\Code\\btc\\Trader\\Data\\slave1_data.csv'
		x=0
		if base:
			with open(dname,'w') as fd:
					writer = csv.writer(fd)
					writer.writerow(['time','low','high','open','close','volume'])
			timer = timein
		else:
			dy = pd.read_csv(dname,error_bad_lines=False)
			dy['time'] = pd.to_datetime(dy['time'],unit='s')
			timer = max((today - max(dy.time)).total_seconds(),60)
		while 3 * x * granul < timer:
			time.sleep(1)
			tdelta = datetime.timedelta(minutes=3 *x *granul)
			x = x + 1
			endtime = today - tdelta
			starttime = endtime - min(datetime.timedelta(minutes=3*granul),datetime.timedelta(seconds=timer))
			try:
				all_data=[]
				data = getProductHistoricRates(product="BTC-USD",start=starttime,end=endtime,granularity=granul)
				for i in data:
					try:
						i = np.array(i)
						all_data.append(i)
					except:
						pass
				with open(dname,'a') as fd:
					for j in all_data:
						writer = csv.writer(fd)
						writer.writerow(j)
			except:
				print('error')

		df2 = pd.read_csv(dname,error_bad_lines=False)
		df2['time'] = pd.to_datetime(df2['time'],unit='s')
		tdelta = datetime.timedelta(seconds=granul)
		mintime = df2['time'].min()
		maxxy = df2['time'].max()
		time_data = []
		j=0
		timev = maxxy
		print ('min ',mintime,'  max',maxxy)
		while timev >= mintime:
			timev = today - tdelta * j
			time_data.append(timev)
			j += 1

		df3 = pd.DataFrame(time_data,columns=['time'])
		df3['time']=pd.to_datetime(df3['time'],unit='s')
		df = pd.merge(df3,df2, on='time', how='left')
		df = df[1:-1]
		df = df.fillna(0)
		collist = ['low','high','open','close','volume']
		df[collist] = df[collist].apply(pd.to_numeric)
		df['time'] = pd.to_datetime(df['time'],unit='s')
		df = df.sort_values(by =['time'])
		for i in collist:
			df[i] = df[i].replace(to_replace=0, method='ffill')
		df['price'] = (df.low + df.high)/2
		df['prof'] = df.price.shift(-30)-df.price -df.price*.005
		df['pshift'] = df.price.shift(-30)
		df['tshift'] = df.time.shift(-30)
		df['take'] = df.apply(lambda x : 1 if  x['prof'] > 0 else 0,axis = 1)
		df['price'] = (df.low + df.high)/2
		df['pdelta'] = df.price - df.price.shift(1)
		Hold_time = (1,5,10,30,60,120,240,480)
		for i in Hold_time:
			n3 = 'vol' + str(i)
			n4 = 'ma' + str(i)
			n5 = 'ma_diff' + str(i)
			n6 = 'volume' + str(i)
			df[n3] = pd.rolling_std(df['pdelta'],i)**2
			df[n4] = pd.Series(df.price).rolling(window=i).mean()
			df[n5] = df.price -df[n4]
			df[n6] = pd.Series(df.volume).rolling(window=i).mean()
		df['ma'] = pd.Series(df.price).rolling(window=5).mean()
		df['ma_diff'] = df.price -df['ma']
		df['volatility']=pd.rolling_std(df['pdelta'],20)**2
		df['uband']=df['ma'] + pd.rolling_std(df.price,20)
		df['bband']=df['ma'] - pd.rolling_std(df.price,20)
		df['u_take']=df.apply(lambda x : 1 if  x['uband'] < x['price'] else 0,axis = 1)
		df['b_take']=df.apply(lambda x : 1 if  x['bband'] > x['price'] else 0,axis = 1)
		return df

	def make_mark(self,product,trade_quant,spread_thresh,order_thresh):
		today = datetime.date.today().strftime("%B %d, %Y")
		name = today + '_Slave1.csv'
		df = mm.preprocessing(base=True,timein=1200,granul=60)
		with open(name,'a') as fd:
			writer = csv.writer(fd)
			writer.writerow(['time','bid','ask','usd_change','btc_change'])
		aggressive = True
		num_trades = 0
		prod_string = product.split('/')[0]+'-'+product.split('/')[1]
		x = cb_balance()
		for i in x:
			if i[0]=='USD':
				starting_usd_balance =float(i[1])
			if i[0] =='BTC':
				starting_btc_balance = float(i[1])
		breaker = 0
		pname = 'slave1_classifier.pickle'
		pickle_in = open('Classifiers/'+ pname,'rb')
		clf = pickle.load(pickle_in)
		trade_list = []
		executed_trades = []
		timer = 0 
		while True:
			timer += 1
			if breaker==1:
				break
			print (cancel_all())
			zzz=0
			USD, bid, ask,b_depth,a_depth,adj_imb = gdax(prod_string)
			if USD ==0:
				break
			start_price = float(USD)
			while True and zzz==0:
				time.sleep(55)
				USD, bid, ask,b_depth,a_depth,adj_imb = gdax(prod_string)
				if USD == 0:
					break
				bid = float(bid)
				ask = float(ask)
				USD = float(USD)
				spread = max(spread_thresh,(ask-bid)/2)
				df = mm.preprocessing(base=False,timein=1200,granul=60)
				Hold_time = (1,5,10,30,60,120,240,480)
				features = ['volatility','ma_diff','pdelta','u_take','b_take','volume']
				for i in Hold_time:
					n3 = 'vol' + str(i)
					n4 = 'ma' + str(i)
					n5 = 'ma_diff' + str(i)
					n6 = 'volume' + str(i)
					features.extend([n3,n4,n5,n6])
				df = df[features]
				df = df[1:]
				df2 = df.tail(1)
				XX = (array(df2[features].values).tolist())
				a = clf.predict(XX)
				print (a)
				if a[:1] == 1:
					num_trades = num_trades + 1
					if aggressive:
						open_bid_price = round(float(ask),2)
					else:
						open_bid_price = round(float(ask-spread),2)
					print ('BUY',cb_trade_agg('buy',trade_quant,open_bid_price,prod_string))

				for i in trade_list:
					if timer - i >= 30:
						if aggressive:
							open_ask_price = round(float(bid),2)
						else:14
							open_ask_price = round(float(bid+spread),2)
						print ('SELL',cb_trade_agg('sell',trade_quant,open_ask_price,prod_string))
						trade_list.remove(i)
						executed_trades.append('Buy ' + str(i))
						executed_trades.append('Sell '+ str(timer))
				x = cb_balance()
				if x == 'ERROR':
					break
				for i in x:
					if i[0]=='USD':
						USD_balance = float(i[1])
					if i[0] =='BTC':
						bitcoin = float(i[1])
				btc_change = bitcoin-starting_btc_balance 
				usd_change = USD_balance-starting_usd_balance
				total_change = usd_change + (btc_change * (bid + ask)/2)
				static_p_balance = USD_balance + bitcoin * start_price
				market_rate = starting_usd_balance + starting_btc_balance*(bid+ask)/2
				timey=datetime.datetime.now().strftime("%I:%M%p %B%d-%Y")
				print ('Time: ',timey,
					'Base Profit - USD',usd_change ,
					'Subset Profit - BTC',btc_change ,
					'Adj Profit',total_change,
					'Number of Trades:',num_trades)
				with open(name,'a') as fd:
					writer = csv.writer(fd)
					writer.writerow([str(timey),str(bid),str(ask),str(usd_change),str(btc_change)])

				if abs(btc_change) > .1 or total_change < -.5 or abs(usd_change)>30:
					breaker=1
					break



	
mm= Slave1()
mm.make_mark('BTC/USD',.02,.01,0)
# da = mm.preprocessing(base=True,timein=1200,granul=60)
# print (len(da))
# da = mm.preprocessing(base=False,timein=1200,granul=60)
# print (len(da))