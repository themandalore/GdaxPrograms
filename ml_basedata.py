'''Machine Learning--strategies'''
'''
Test bollinger bands (optimize band width)
	- optimize hold Time
	-band to buy, band to sell 


'''



from sklearn import preprocessing, cross_validation, svm
from sklearn.cross_validation import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from pandas import *
import pandas as pd
import numpy as np
from numpy import array
import pickle, math, warnings
from operator import itemgetter, attrgetter, methodcaller
warnings.filterwarnings("ignore", category=DeprecationWarning) 

directory = 'C:\\Code\\btc\\Trader\\Data\\'
'''
Use prices.csv when ready
'''

Hold_time = (1,5,10,30,60,120,240,480)

directory ='C:\\Code\\btc\\Trader\\Data\\'
classified = 'gdax_60_fmt' +'.csv'
df = pd.DataFrame.from_csv(directory + classified)
df['time'] = pd.to_datetime(df['time'])
df = df.sort(['time'])
df = df.tail(50000)
df['price'] = (df.low + df.high)/2
df['pdelta'] = df.price - df.price.shift(1)
for i in Hold_time:
	n1 = 'take'+ str(i)
	n2 = 'prof'+ str(i)
	n3 = 'vol' + str(i)
	n4 = 'ma' + str(i)
	n5 = 'ma_diff' + str(i)
	n6 = 'volume' + str(i)
	df[n1] = df.price.shift(-i)-df.price -df.price*.005
	df[n2] = df.apply(lambda x : 1 if  x[n1] > 1 else 0,axis = 1)
	df[n3] = pd.rolling_std(df['pdelta'],i)**2
	df[n4] = pd.rolling_mean(df.price,i)
	df[n5] = df.price -df[n4]
	df[n6] = pd.rolling_mean(df.volume,i)
df['ma'] = pd.rolling_mean(df.price,5)
df['ma_diff'] = df.price -df['ma']
df['volatility']=pd.rolling_std(df['pdelta'],20)**2
df['uband']=df['ma'] + pd.rolling_std(df.price,20)
df['bband']=df['ma'] - pd.rolling_std(df.price,20)
df['u_take']=df.apply(lambda x : 1 if  x['uband'] < x['price'] else 0,axis = 1)
df['b_take']=df.apply(lambda x : 1 if  x['bband'] > x['price'] else 0,axis = 1)
# df.to_csv(directory + '_ready_'+classified)



newtimes = (30,480)
for ii in newtimes:
	to_predict = 'take'+str(ii)
	proffy = 'prof'+str(ii)
	features = ['volatility','ma_diff','pdelta','u_take','b_take','volume']
	for i in Hold_time:
		n1 = 'take'+ str(i)
		n2 = 'prof'+ str(i)
		n3 = 'vol' + str(i)
		n4 = 'ma' + str(i)
		n5 = 'ma_diff' + str(i)
		n6 = 'volume' + str(i)
		features.extend([n3,n4,n5,n6])
	print (features)
	cols = np.array(features)
	cols = np.append(cols,to_predict)
	data_df=df[cols]
	#print (data_df.head())
	dfc = df.reset_index()
	dfb = dfc.reindex(np.random.permutation(df.index))
	dfc = dfb[cols]
	dfc.fillna(value=-99999, inplace=True)
	dfc['cb_take']=dfc.apply(lambda x : 1 if  x[to_predict] > 0 else 0,axis = 1)
	dfx = dfc[features]
	print (dfx.head())
	X = np.array(dfx)
	y = np.array(dfc['cb_take'])
	z = np.array(dfc[to_predict])
	print (y)
	names = np.array(dfc.columns.values)
	opps=dfc['cb_take'].sum(axis=0)
	print (opps)



	# clf = RandomForestClassifier(n_estimators=100,n_jobs=-1)
	# clf.fit(X,y)
	# X_selected = clf.transform(X)
	# feat_list = sorted(zip(map(lambda x: round(x, 4), clf.feature_importances_), names), 
	#              reverse=True)
	# print (feat_list)
	# good_feats = []
	# for i in feat_list:
	# 	array = np.asarray(i)
	# 	if array[1] == 'index':
	# 		pass
	# 	else:
	# 		good_feats.append(array[1])

	# print (good_feats)

	# dfx = dfc[good_feats]
	#X = np.array(dfx)

	eval_size = .3
	kf = StratifiedKFold(y,round(1./eval_size))
	train_indices, valid_indices = next(iter(kf))
	X_train, y_train = X[train_indices], y[train_indices]
	X_test, y_test, z_test = X[valid_indices],y[valid_indices],z[valid_indices]
	#X_train, X_test, y_train, y_test = cross_validation.train_test_split(X,y,test_size = .3)

	test_size=np.shape(X_test)[0]
	print ('Test size: ',test_size)
	numbers = (.001,.01,1,10,100)
	max_c=0
	maxxy=0
	print (X_test[-1])
	for i in numbers:
	    svc = svm.SVC(kernel='rbf',C=i).fit(X_train.astype(int), y_train.astype(int))
	    correct_count=0
	    loop = 0
	    while loop < test_size:
	        if (svc.predict(X_test[loop])[0] - y_test[loop]) == 0:
	            correct_count = correct_count + 1
	            loop = loop + ii - 1
	        loop = loop + 1
	    # print("C- " ,i, ":" ,(correct_count*100/test_size))
	    if correct_count >= maxxy:
	        maxxy=correct_count
	        max_c=i
	print (max_c,'--',maxxy)

	clf= svm.SVC(kernel='rbf', C=max_c,class_weight=None).fit(X_train.astype(int), y_train.astype(int))

	if ii == 30:
		pname = 'Classifiers/slave1_classifier.pickle'
		with open(pname,'wb') as f:
			pickle.dump(clf,f)


	accuracy = clf.score(X_test.astype(int),y_test.astype(int))
	correctbuy = 0
	buymiss = 0
	wrongbuy = 0

	adj_profit = 0
	loop = 0 
	while loop < len(X_test):
		temp = X_test[loop]
		temp = np.array(temp).reshape((1, -1))
		if clf.predict(temp)[0] == 1 or y_test[loop]==1 :
			if y_test[loop]==1 and  clf.predict(temp)[0] == 1:
				correctbuy = correctbuy + 1
				#loop = loop + ii
				if loop >= len(X_test):
					loop = len(X_test)-1
				adj_profit = adj_profit + z_test[loop]
			elif y_test[loop]==1 and  clf.predict(temp)[0] == 0:
				buymiss = buymiss +1
			elif y_test[loop]==0 and  clf.predict(temp)[0] == 1:
				wrongbuy = wrongbuy +1
				adj_profit = adj_profit + z_test[loop]
				#loop = loop + ii
				if loop >= len(X_test):
					loop = len(X_test)-1
		loop = loop + 1
	print ('HOLD TIME -',ii)
	print ('Wrongbuy',wrongbuy)
	print ('buymiss',buymiss)
	print ('Correctbuy',correctbuy)
	if buymiss == 0:
		buymiss ==1

	print ('Accuracy', accuracy,' / Length of Dataset',len(dfc))
	print ('Time in Dataset',round(len(X_test)/60/24,2),'days  /','Number of Opportunities',correctbuy+wrongbuy+buymiss)
	print ('Expected Profit: ', ((correctbuy-wrongbuy)/(correctbuy+wrongbuy+buymiss)) * (dfb[dfb[proffy]>0].sum()[proffy]))
	print ('Adjusted Profit: ',adj_profit)
#this treats each row as a day and pushes it back for graphing purposes
'''
lin_svc = svm.LinearSVC(C=1).fit(X,y)
a = lin_svc.predict(XX)
ndarr = np.asarray(a) # if ndarr is actually an array, skip this
fast_df = pd.DataFrame({"new_type": ndarr.ravel()})
a.tolist()b
data_dfm['new_type'] =  fast_df['new_type']
data_dfm.to_csv('final_learned.csv')
'''