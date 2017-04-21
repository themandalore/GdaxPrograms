'''
Take cb data and figure out:
Best time frame for moving average prediction
-apply to market making program
then do:
machine learning for price prediction
'''
import pandas as pd
import numpy as np
import datetime

directory = 'C:\\Code\\btc\\Trader\\Data\\'


def min_anal(name):
	df = pd.DataFrame.from_csv(name)
	df['time'] = pd.to_datetime(df['time'])
	df['price'] = (df.low + df.high)/2
	df = df.dropna()
	maxtime = df['time'].max()
	mintime = df['time'].min()
	time_delta = maxtime-mintime
	if time_delta.days > 0:
		days = time_delta.days
	else:
		days = 1
	time_range = [1,15,30,60,120,480]
	fee = .0025
	test_range =[.1,2,5,10,20]
	print ('Check text file for ouptut')
	f = open('cb_analysis.txt', 'w')
	for j in test_range:
		for i in time_range:
			n1 = 'p_delta_'+ str(i)
			n2 = 'ma_'+str(i)
			n3='ma_diff_'+str(i)
			n4='buy_vol_'+str(i)
			n8='sell_vol_'+str(i)
			n5 = 'volatility'+str(i)
			n6 = 'u_thresh'+str(i)+str(j)
			n7 = 'l_thresh'+str(i)+str(j)
			n9 = 'cost' + str(i) + str(j)
			df[n1] = df.price - df.price.shift(i)
			df[n2] = pd.rolling_mean(df.price,i)
			df[n3] = df.price -df[n2]
			df['squared']=df[n1]*df[n1]
			df[n5]=pd.rolling_mean(df['squared'],i)
			df[n6]=df[n2] + pd.rolling_std(df.price,i)*j
			df[n7]=df[n2] - pd.rolling_std(df.price,i)*j
			df['fee']=df['price']*fee
			df[n4] = df.apply(lambda x : x['p_delta_1'] if  x['price'] > x[n6] else -1*x['p_delta_1'] if x['price'] < x[n7] else 0,axis = 1)
			df[n8] = df.apply(lambda x : x['p_delta_1'] if  x['price'] < x[n6] else -1*x['p_delta_1'] if x['price'] > x[n7] else 0,axis = 1)
			df['dummy_n4'] = df.apply(lambda x : 1 if  x['price'] > x[n6] or x['price'] < x[n7] else 0,axis = 1)
			df['dummy2'] =abs(df['dummy_n4']-df['dummy_n4'].shift(1))
			df[n9] = df.apply(lambda x : x['fee'] if x['dummy2'] > 0 else 0,axis = 1)
			prof_buyvol = df[n4].sum(axis=0)
			prof_sellvol = df[n8].sum(axis=0)
			scount = (df[df[n9] > 0][n9].sum(axis=0))/fee
			cost = df[n9].sum(axis=0)
			Adj_prof_b = prof_buyvol - cost
			Adj_prof_s = prof_sellvol - cost
			output= ' '.join(['Test Range ', str(j),' Profit: ',str(i),': buy:',str(prof_buyvol),'sell:',str(prof_sellvol),' | Days:',str(days), '  Adj_prof: buy: ',str(Adj_prof_b),'sell: ',str(Adj_prof_s) , 'tradecount ',str(scount)])
			f.write(output)
			print (output)
	for j in test_range:
		for i in time_range:
			n9 = 'cost' + str(i) + str(j)
			n10 = 'timeheld' + str(i) + str(j)
			df2 = df.loc[df[n9] > 0]
			if len(df2) > 0:
				df2[n10] = df2['time'] - df2['time'].shift(-1)
				timeheld = df2[n10].mean(axis=0)
				print ('avg timeheld:',i,' ',j,': ',timeheld)
	newname = newname = directory+'gdax_'+ str(60) +'_analysis.csv'
	df.to_csv(newname)
	print ('Obs:',len(df))
	print (df.head())
	f.close()


def sec_anal(name, granul):
	df = pd.read_csv(name,error_bad_lines=False)
	df2 = pd.DataFrame(df)
	df2['time'] = pd.to_datetime(df2['time'],unit='s')
	df2.dropna()
	mintime = df2['time'].min()
	today = df2['time'].max()
	print (df2.tail())
	#today = datetime.datetime.now().replace(microsecond=0)
	tdelta = datetime.timedelta(seconds=granul)
	time_data = []
	j=0
	time = today
	while time >= mintime:
		time = today - tdelta * j
		time_data.append(time)
		j = j + 1

	df3 = pd.DataFrame(time_data,columns=['time'])

	df3['time']=pd.to_datetime(df3['time'],unit='s')
	res = pd.merge(df3,df2, on='time', how='left')
	res['volume']= res.apply(lambda x : x['volume'] if  x['volume'] > 0 else 0,axis = 1)
	res.sort(['time'])
	res.fillna(method='ffill', inplace=True)
	print (res.head())
	'''collist = ('low','high','open','close')
	for i in collist:
		#res[i]=res[i].astype(int)
		minny = res[i].min(axis=0)
		print (minny)
		y = 1
		while minny < 1:
			res['h2']=res[i].shift(y)
			res[i]= res.apply(lambda x : x[i] if  x[i] > 0 else x['h2'],axis = 1)
			minny = res[i].min(axis=0)
			y = y + 1
	'''
	newname = directory+'gdax_'+ str(60) +'_fmt.csv'
	res.to_csv(newname)
	return res
	#'volume'=0
directory = 'C:\\Code\\btc\\Trader\\data\\'
name = directory+'gdax_'+ str(60) +'.csv'
print (name)
res = sec_anal(name,60)
print (res.head())
print (res.tail())
# print (len(res))


#min_anal(name)