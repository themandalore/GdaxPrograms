 
import sys
import time, json, requests, csv, datetime
import pandas as pd
import numpy as np
 
 
url="https://api.gdax.com"
product_id="BTC-USD"
 
today = datetime.datetime.now()

 
 
 
titles = ('time','low','high','open','close','volume')

 
 
def getProductHistoricRates(product='', start='', end='', granularity=''):
	payload = { "start" : start, "end" : end,"granularity" : granularity}
	response = requests.get(url + '/products/%s/candles' % (product), params=payload)
	return response.json()
	 

def getdata(granul,name):
	lenny=1
	x=0
	y=0
	total_len = 0
	three_hours = datetime.timedelta(minutes=3*granul)
	with open(name,'w') as fd:
			writer = csv.writer(fd)
			writer.writerow(['time','low','high','open','close','volume'])
	while lenny > 0 or y<50 :
		x = x + 1
		tdelta = datetime.timedelta(minutes=3 *x *granul)
		endtime = today - tdelta
		starttime = endtime - three_hours
		try:
			all_data =[]
			data = getProductHistoricRates(product=product_id,start=starttime,end=endtime,granularity=granul)
			for i in data:
				try:
					all_data.append(i)
					y = 0
				except:
					pass
			with open(name,'a') as fd:
				for j in all_data:
					writer = csv.writer(fd)
					writer.writerow(j)
			y = y + 1
			lenny = len(data)
			total_len += lenny
			if total_len > 50000:
				y = 100
		except:
			pass
		if lenny == 0:
			y = y + 1
		print ('Data:',lenny,'_',starttime,'_',endtime)
		time.sleep(1)

	print ('y=',y)

'''
Next, fill in seconds that are missing in the data
'''
directory = 'C:\\Code\\btc\\Trader\\data\\'
name = directory+'gdax_second'+'.csv'
#getdata(1,name)

print (name)
df = pd.read_csv(name,error_bad_lines=False)
df = pd.DataFrame(df)
print (df.head())
try:
	df['time']=pd.to_datetime(df['time'],format="%Y-%m-%d %H:%M:%S")
except:
	df['time']=df['time'].astype('int').astype("datetime64[s]")

print (len(df))
df.to_csv(name)


def sec_anal(name, granul):
	df = pd.read_csv(name,error_bad_lines=False)
	df2 = pd.DataFrame(df)
	df['time']=pd.to_datetime(df['time'],format="%Y-%m-%d %H:%M:%S")
	df2 = df2.sort(['time'])
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
print (name)
res = sec_anal(name,1)
print (res.head())
print (res.tail())